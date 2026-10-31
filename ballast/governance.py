"""Governance branches: announced re-teams (watcher set, admin set), the wind-down, and a holder's redemption.

Rotation (architecture: role map, "owner"): the bot co-signs a `set_team` that moves the freezer or the admin only if
B announced the new set on chain first — `BALLAST/1|watchers|a=<asset>|t=<t>|m=<ss58,…>` or
`BALLAST/1|admins|a=<asset>|t=<t>|m=<ss58,…>`, signed by B itself — at least K blocks before the co-signature, and
the proposed account IS that set's multisig address. One role per rotation; the issuer always stays M_mint. A new
admin set must contain B with a threshold >= 2, so no admin set can thaw without the bot or a second key.

Wind-down (spec.md, "Shortfall end state"): after the asset has been frozen for >= W blocks with the shortfall
confirmed, watchers freeze every holder with a balance (`freeze(who)`), B posts `BALLAST/1|final|a=<asset>|r=<r>`,
and the bot co-signs the asset thaw only when every holder with a balance is individually frozen. A watcher then
re-freezes the asset only while some holder with a balance is still unfrozen (`winddown_hold`). A holder asks first
(`BALLAST/1|redeem|a=<asset>|evm=<0x…>`, signed by that holder); the admin answers with ONE atomic
`utility.batch_all([assets.thaw(who), assets.burn(who, balance)])` and the custodian releases r x balance on the
reserve chain with `redeemId = redeem_id(<request extrinsic id>)`.

Gates here are pure (`(sign, reason)`); `ballast/bot.py` wraps them as its `Gate`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from .chain_profile import blake2_256
from .multisig import multi_address, public_key
from .remarks import block_remarks, encode, parse

ANNOUNCE_ROLE = {"watchers": "freezer", "admins": "admin"}  # announcement kind -> the team role it may move
FROZEN_STATUSES = ("Frozen", "Blocked")  # an individually frozen asset account
EVM_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")


def _same(a: str | None, b: str | None) -> bool:
    try:
        return a is not None and b is not None and public_key(a) == public_key(b)
    except (ValueError, TypeError):
        return False


# --- remark texts --------------------------------------------------------------------------------------------
def announcement_text(kind: str, asset_id: int, threshold: int, members: list[str]) -> str:
    if kind not in ANNOUNCE_ROLE:
        raise ValueError(f"unknown announcement kind {kind!r} (watchers | admins)")
    if not members or len({public_key(m) for m in members}) != len(members):
        raise ValueError("members must be distinct accounts")
    return encode(kind, a=asset_id, t=threshold, m=",".join(members))


def final_text(asset_id: int, r: Decimal | str) -> str:
    r = Decimal(str(r))
    if not Decimal(0) <= r < Decimal(1):
        raise ValueError(f"haircut r={r} must be in [0, 1): a wind-down only runs on a shortfall")
    return encode("final", a=asset_id, r=f"{r:.4f}")


def redeem_text(asset_id: int, evm: str) -> str:
    if not EVM_ADDRESS.match(evm):
        raise ValueError(f"not an EVM address: {evm!r}")
    return encode("redeem", a=asset_id, evm=evm)


def redeem_id(extrinsic_id: str) -> bytes:
    """The vault's `redeemId` for a redemption request: blake2_256("ballast:redeem:<block>-<index>")."""
    return bytes.fromhex(blake2_256(f"ballast:redeem:{extrinsic_id}".encode())[2:])


# --- reading remarks back --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Posted:
    """One BALLAST/1 remark found on chain by its extrinsic id, with who sent it."""

    extrinsic_id: str
    block_number: int
    signer: str
    sender: str
    text: str
    fields: dict


def read_remark(substrate: Any, extrinsic_id: str) -> Posted | None:
    """The BALLAST/1 remark of extrinsic `<block>-<index>` (one with a System.Remarked event), or None."""
    number, _, index = extrinsic_id.partition("-")
    if not number.isdigit() or not index.isdigit():
        raise ValueError(f"not an extrinsic id: {extrinsic_id!r}")
    block_hash = substrate.get_block_hash(int(number))
    if block_hash is None:
        return None
    for rem in block_remarks(substrate, block_hash):
        if rem["extrinsic_index"] == int(index):
            try:
                fields = parse(rem["text"])
            except ValueError:
                return None
            return Posted(extrinsic_id, int(number), rem["signer"], rem["sender"], rem["text"], fields)
    return None


@dataclass(frozen=True)
class Announcement:
    kind: str
    asset_id: int
    threshold: int
    members: tuple[str, ...]
    address: str  # the announced set's multisig address
    block_number: int
    extrinsic_id: str
    signer: str


def announcement_of(posted: Posted, ss58_format: int = 42) -> Announcement:
    f = posted.fields
    if f.get("type") not in ANNOUNCE_ROLE:
        raise ValueError(f"{posted.extrinsic_id} is a {f.get('type')!r} remark, not an announcement")
    try:
        asset_id, threshold = int(f["a"]), int(f["t"])
        members = tuple(m for m in f["m"].split(",") if m)
        address = multi_address(list(members), threshold, ss58_format=ss58_format)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{posted.extrinsic_id}: malformed announcement ({exc})") from exc
    return Announcement(f["type"], asset_id, threshold, members, address, posted.block_number, posted.extrinsic_id,
                        posted.signer)


# --- rotation -------------------------------------------------------------------------------------------------
def rotation_gate(current: dict, proposed: dict, *, breaker: int, m_mint: str, m_admin: str, b: str,
                  announcement: Announcement | None, head: int, k: int) -> tuple[bool, str] | None:
    """None = the proposal moves neither the freezer nor the admin (the plain set_team gate applies)."""
    if not _same(proposed.get("issuer"), m_mint) or not _same(current.get("issuer"), m_mint):
        return False, f"issuer must stay M_mint {m_mint}"
    changed = [role for role in ("admin", "freezer") if not _same(proposed.get(role), current.get(role))]
    if not changed:
        return None
    if len(changed) > 1:
        return False, "admin and freezer would both change: one announced rotation per set_team"
    role = changed[0]
    kind = next(k_ for k_, r in ANNOUNCE_ROLE.items() if r == role)
    if role == "freezer" and not _same(proposed.get("admin"), m_admin):
        return False, f"admin must stay M_admin {m_admin} while the watcher set rotates"
    if announcement is None:
        return False, (f"the {role} would change without an announcement (a B-signed BALLAST/1|{kind} remark "
                       f">= K = {k} blocks earlier)")
    a = announcement
    if a.kind != kind:
        return False, f"{a.extrinsic_id} announces {a.kind}, but the proposal moves the {role}"
    if a.asset_id != breaker:
        return False, f"{a.extrinsic_id} announces a set for asset {a.asset_id}, not {breaker}"
    if not _same(a.signer, b):
        return False, f"{a.extrinsic_id} is signed by {a.signer}, not the bot key B"
    if not _same(a.address, proposed.get(role)):
        return False, f"proposed {role} {proposed.get(role)} is not the announced set's address {a.address}"
    if role == "freezer" and a.threshold != 1:
        return False, f"a watcher set is 1-of-N (any one watcher freezes); announced t={a.threshold}"
    if role == "admin":
        if not any(_same(m, b) for m in a.members) or not 2 <= a.threshold <= len(a.members):
            return False, "an admin set must include B with a threshold >= 2 (no thaw without two keys)"
    age = head - a.block_number
    if age < k:
        return False, f"announced at #{a.block_number}, {age} blocks ago < K = {k}: too early"
    return True, (f"{role} -> the {kind} set announced by B at {a.extrinsic_id} (t={a.threshold}, "
                  f"{len(a.members)} members), {age} >= K = {k} blocks ago")


# --- wind-down ------------------------------------------------------------------------------------------------
def holders(substrate: Any, asset_id: int, block_hash: str | None = None) -> list[dict]:
    """Every account of the asset: {"who", "balance", "status", "frozen"}."""
    out = []
    for key, value in substrate.query_map("Assets", "Account", [asset_id], block_hash=block_hash, page_size=200):
        v = value.value
        status = v.get("status")
        status = next(iter(status)) if isinstance(status, dict) else status
        out.append({"who": key.value if hasattr(key, "value") else key, "balance": int(v["balance"]),
                    "status": status, "frozen": status in FROZEN_STATUSES})
    return out


def winddown_hold(rows: list[dict]) -> bool:
    """True when re-freezing the asset would change nothing: every holder with a balance is individually frozen."""
    with_balance = [h for h in rows if h["balance"] > 0]
    return bool(with_balance) and all(h["frozen"] for h in with_balance)


def final_of(posted: Posted | None, *, breaker: int, b: str) -> tuple[Decimal | None, str]:
    if posted is None:
        return None, "no BALLAST/1|final remark found"
    f = posted.fields
    if f.get("type") != "final" or f.get("a") != str(breaker):
        return None, f"{posted.extrinsic_id} is not a final remark for asset {breaker}"
    if not (_same(posted.signer, b) and _same(posted.sender, b)):
        return None, f"{posted.extrinsic_id} is not signed by the bot key B"
    try:
        r = Decimal(f["r"])
    except (KeyError, InvalidOperation):
        return None, f"{posted.extrinsic_id}: no valid haircut r"
    if not Decimal(0) <= r < Decimal(1):
        return None, f"{posted.extrinsic_id}: haircut r={r} outside [0, 1)"
    return r, f"final r={r} posted by B at {posted.extrinsic_id}"


def winddown_gate(frozen: bool, final: Posted | None, rows: list[dict], *, breaker: int, b: str,
                  freeze_block: int | None, w: int) -> tuple[bool, str]:
    """Thaw gate, wind-down branch: frozen for >= W blocks before `final`, `final` by B, every holder frozen."""
    if not frozen:
        return False, "the breaker asset is not frozen"
    r, why = final_of(final, breaker=breaker, b=b)
    if r is None:
        return False, why
    if freeze_block is None:
        return False, "the freeze could not be located: cannot tell how long the asset has been frozen"
    if final.block_number - freeze_block < w:
        return False, (f"final posted {final.block_number - freeze_block} blocks after the freeze #{freeze_block} "
                       f"< W = {w}: too early for a wind-down")
    with_balance = [h for h in rows if h["balance"] > 0]
    if not with_balance:
        return False, "no holder has a balance: nothing to wind down"
    open_ = [h["who"] for h in with_balance if not h["frozen"]]
    if open_:
        return False, f"{len(open_)} of {len(with_balance)} holders with a balance are not individually frozen"
    return True, (f"wind-down: {why}, {final.block_number - freeze_block} >= W = {w} blocks after the freeze, all "
                  f"{len(with_balance)} holders with a balance individually frozen")


def redeem_gate(request: Posted | None, final: Posted | None, row: dict | None, asset_frozen: bool, *,
                breaker: int, b: str, holder: str, amount: int) -> tuple[bool, str]:
    """Co-sign batch_all([thaw(holder), burn(holder, amount)]) iff the holder asked first and burns everything."""
    r, why = final_of(final, breaker=breaker, b=b)
    if r is None:
        return False, why
    if request is None:
        return False, "no BALLAST/1|redeem request found"
    f = request.fields
    if f.get("type") != "redeem" or f.get("a") != str(breaker) or not EVM_ADDRESS.match(f.get("evm", "")):
        return False, f"{request.extrinsic_id} is not a redeem request for asset {breaker}"
    if not (_same(request.signer, holder) and _same(request.sender, holder)):
        return False, f"{request.extrinsic_id} is not signed by the holder {holder}"
    if asset_frozen:
        return False, "the asset is still frozen: the wind-down thaw comes first (a burn would fail inside it)"
    if row is None or row["balance"] <= 0:
        return False, f"{holder} holds nothing of asset {breaker}"
    if not row["frozen"]:
        return False, f"{holder} is not individually frozen: the wind-down has not reached this account"
    if amount != row["balance"]:
        return False, f"burn amount {amount} != the holder's whole balance {row['balance']}"
    return True, (f"redeem: {request.extrinsic_id} by the holder, {why}; burn {amount} and release "
                  f"r x amount = {int(r * amount)} to {f['evm']}")
