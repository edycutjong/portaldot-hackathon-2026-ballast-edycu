"""Portaldot connection + extrinsic submission with receipts that name the chain profile."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from substrateinterface import Keypair, SubstrateInterface

from .chain_profile import Profile, require_standin
from .dispatch import Outcome, extrinsic_outcome, multisig_inner_results
from .types_1002 import patch_assets_balance_u64


WS_TIMEOUT_S = 60


class _Substrate1002(SubstrateInterface):
    """Re-applies the spec-1002 Assets u64 patch whenever the SDK (re)loads runtime metadata."""

    def init_runtime(self, *args, **kwargs):
        result = super().init_runtime(*args, **kwargs)
        if self.metadata is not None:
            patch_assets_balance_u64(self.metadata)
        return result


def connect(profile: Profile, url: str) -> SubstrateInterface:
    cls = _Substrate1002 if profile.patch_assets_u64 else SubstrateInterface
    # A socket timeout: a node that stops answering raises instead of hanging a watcher forever.
    kwargs: dict[str, Any] = {"url": url, "ws_options": {"timeout": WS_TIMEOUT_S}}
    if profile.type_registry_preset:
        kwargs["type_registry_preset"] = profile.type_registry_preset
    substrate = cls(**kwargs)
    substrate.init_runtime()
    return substrate


def dev_keypair(profile: Profile, uri: str) -> Keypair:
    """Deterministic dev URI (e.g. //BallastA). Public seeds: stand-in profiles only."""
    require_standin(profile)
    if not uri.startswith("//"):
        raise ValueError("dev keys are //Name URIs")
    return Keypair.create_from_uri(uri)


def _jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, default=str))


@dataclass
class Receipt:
    profile: str
    step: str
    call: str
    signer: str
    block_number: int
    block_hash: str
    extrinsic_index: int
    extrinsic_hash: str
    outcome: Outcome
    inner: list[Outcome] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)

    @property
    def extrinsic_id(self) -> str:
        return f"{self.block_number}-{self.extrinsic_index}"

    def event_names(self) -> list[str]:
        return [f"{e['module_id']}.{e['event_id']}" for e in self.events]

    def as_dict(self) -> dict:
        return {
            "profile": self.profile,
            "step": self.step,
            "call": self.call,
            "signer": self.signer,
            "extrinsic_id": self.extrinsic_id,
            "block_number": self.block_number,
            "block_hash": self.block_hash,
            "extrinsic_index": self.extrinsic_index,
            "extrinsic_hash": self.extrinsic_hash,
            "outcome": self.outcome.as_dict(),
            "inner": [o.as_dict() for o in self.inner],
            "events": self.events,
        }


def submit(
    substrate: SubstrateInterface,
    profile: Profile,
    signer: Keypair,
    module: str,
    function: str,
    params: dict,
    *,
    step: str,
    call_label: str | None = None,
) -> Receipt:
    """Sign, submit, wait for inclusion; decode the outcome from the chain's metadata. Never raises on Err."""
    ensure_connected(substrate)
    call = substrate.compose_call(call_module=module, call_function=function, call_params=params)
    extrinsic = substrate.create_signed_extrinsic(call=call, keypair=signer)
    result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    events = [_jsonable(e.value) for e in result.triggered_events]
    block_number = substrate.get_block_number(result.block_hash)
    return Receipt(
        profile=profile.name,
        step=step,
        call=call_label or f"{module}.{function}",
        signer=signer.ss58_address,
        block_number=block_number,
        block_hash=result.block_hash,
        extrinsic_index=result.extrinsic_idx,
        extrinsic_hash=result.extrinsic_hash,
        outcome=extrinsic_outcome(events, substrate.metadata),
        inner=multisig_inner_results(events, substrate.metadata),
        events=[{k: e[k] for k in ("module_id", "event_id", "attributes")} for e in events],
    )


def find_receipt(
    substrate: SubstrateInterface,
    profile: Profile,
    signer: str,
    module: str,
    function: str,
    *,
    step: str,
    from_block: int,
    to_block: int | None = None,
    call_args: dict | None = None,
) -> Receipt | None:
    """Rebuild the receipt of an extrinsic that landed but was never recorded (a run that crashed after `submit`).

    Scans blocks from_block..to_block (default: head) for the first extrinsic signed by `signer` calling
    module.function (and, if given, whose call arguments include `call_args`), and decodes its outcome from that
    block's events exactly like `submit`."""
    head = substrate.get_block_number(None) if to_block is None else to_block
    for number in range(from_block, head + 1):
        block_hash = substrate.get_block_hash(number)
        for idx, ext in enumerate(substrate.get_extrinsics(block_hash=block_hash)):
            v = ext.value
            if v.get("address") != signer or (v["call"]["call_module"], v["call"]["call_function"]) != (module, function):
                continue
            got = {a["name"]: a["value"] for a in v["call"].get("call_args", [])}
            if any(got.get(k) != want for k, want in (call_args or {}).items()):
                continue
            events = [_jsonable(e.value) for e in substrate.get_events(block_hash)
                      if e.value.get("extrinsic_idx") == idx]
            return Receipt(
                profile=profile.name, step=step, call=f"{module}.{function}", signer=signer,
                block_number=number, block_hash=block_hash, extrinsic_index=idx,
                extrinsic_hash=v.get("extrinsic_hash") or "", outcome=extrinsic_outcome(events, substrate.metadata),
                inner=multisig_inner_results(events, substrate.metadata),
                events=[{k: e[k] for k in ("module_id", "event_id", "attributes")} for e in events],
            )
    return None


def ensure_connected(substrate: SubstrateInterface) -> None:
    """Reopen the websocket if the node dropped it. Public nodes close idle sockets — e.g. while a drill waits on a
    subprocess — and the next query then fails on an empty frame."""
    try:
        substrate.rpc_request("system_health", [])
    except Exception:  # noqa: BLE001 — any transport failure: reconnect once, let the real call raise if it persists
        substrate.connect_websocket()
