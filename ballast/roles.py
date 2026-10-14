"""The role map — the product. Who may do what on the breaker asset (asset 1) and the control asset (asset 2).

Breaker asset (asset 1):
  owner  = issuer = M_mint   2-of-2 {A operator, B reserve bot}   mint only with the bot's co-signature
  admin           = M_admin  2-of-3 {A, A2 cold key, B}           thaw needs two signatures
  freezer         = M_watch  1-of-N {W1, …, Wn}                   any one watcher freezes; nothing else
Control asset (asset 2): minted once (S2), then every role moves to a KEYLESS account derived publicly as
blake2_256("ballast:a2-<role>:v1") — nobody can mint, thaw or re-team it again, so S2 is fixed forever.

`audit_team` compares an asset's on-chain team with the role map and names every difference ("DISARMED"):
watchers and `ballast verify` judge on WHAT changed, not on who signed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from scalecodec.utils.ss58 import ss58_encode

from .multisig import multi_address, public_key

KEYLESS_ROLES = ("owner", "issuer", "admin", "freezer")
DEPLOYMENTS = Path(__file__).resolve().parent.parent / "deployments"


def keyless_account(role: str, asset_tag: str = "a2") -> bytes:
    """A public, keyless account: nobody holds a private key for blake2_256("ballast:<tag>-<role>:v1")."""
    if role not in KEYLESS_ROLES:
        raise ValueError(f"unknown role {role!r}")
    return hashlib.blake2b(f"ballast:{asset_tag}-{role}:v1".encode(), digest_size=32).digest()


def same(a: str | None, b: str | None) -> bool:
    return a is not None and b is not None and public_key(a) == public_key(b)


@dataclass(frozen=True)
class RoleMap:
    a: str  # operator
    a2: str  # cold key (emergency path with A)
    b: str  # reserve bot
    watchers: tuple[str, ...]
    ss58_format: int = 42
    watch_threshold: int = 1
    m_mint: str = field(init=False)
    m_admin: str = field(init=False)
    m_watch: str = field(init=False)
    control: dict = field(init=False)

    def __post_init__(self):
        if self.watch_threshold != 1:
            raise ValueError("the watcher set is 1-of-N: any one watcher freezes (as_multi_threshold_1)")
        if len({public_key(x) for x in (self.a, self.a2, self.b)}) != 3:
            raise ValueError("A, A2 and B must be three different keys")
        if not self.watchers:
            raise ValueError("at least one watcher")
        fmt = self.ss58_format
        object.__setattr__(self, "m_mint", multi_address([self.a, self.b], 2, ss58_format=fmt))
        object.__setattr__(self, "m_admin", multi_address([self.a, self.a2, self.b], 2, ss58_format=fmt))
        object.__setattr__(self, "m_watch", multi_address(list(self.watchers), 1, ss58_format=fmt))
        object.__setattr__(self, "control", {r: ss58_encode(keyless_account(r), ss58_format=fmt) for r in KEYLESS_ROLES})

    @property
    def mint_signatories(self) -> list[str]:
        return [self.a, self.b]

    @property
    def admin_signatories(self) -> list[str]:
        return [self.a, self.a2, self.b]

    def breaker_team(self) -> dict[str, str]:
        return {"owner": self.m_mint, "issuer": self.m_mint, "admin": self.m_admin, "freezer": self.m_watch}

    def control_team(self) -> dict[str, str]:
        return dict(self.control)

    def as_dict(self) -> dict:
        return {
            "A": self.a, "A2": self.a2, "B": self.b, "watchers": list(self.watchers), "ss58_format": self.ss58_format,
            "M_mint": {"address": self.m_mint, "threshold": 2, "signatories": ["A", "B"]},
            "M_admin": {"address": self.m_admin, "threshold": 2, "signatories": ["A", "A2", "B"]},
            "M_watch": {"address": self.m_watch, "threshold": 1, "signatories": [f"W{i}" for i in
                                                                                 range(1, len(self.watchers) + 1)]},
            "control_keyless": {r: {"address": a, "derivation": f'blake2_256("ballast:a2-{r}:v1")'}
                                for r, a in self.control.items()},
        }


def audit_team(details: dict | None, expected: dict[str, str]) -> list[str]:
    """Every role of an `Assets.Asset` entry that differs from the expected team. Empty = ARMED as designed."""
    if not details:
        return ["asset does not exist"]
    return [f"{role} is {details.get(role)}, expected {want}" for role, want in expected.items()
            if not same(details.get(role), want)]


@dataclass
class Deployment:
    """Public facts of one role-split deployment (no keys): written by scripts/setup_roles.py, read by the CLI."""

    profile: str
    genesis_hash: str
    breaker: int
    control: int
    decimals: int
    s2: int
    roles: dict
    reserve: dict  # label, evm_chain_id, vault, token
    oracle: dict | None = None
    created_at: str = ""
    setup_evidence: str = ""

    def save(self, path: Path | None = None) -> Path:
        path = path or DEPLOYMENTS / f"{self.profile}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2) + "\n")
        return path

    @classmethod
    def load(cls, profile: str, path: str | Path | None = None) -> "Deployment":
        p = Path(path) if path else DEPLOYMENTS / f"{profile}.json"
        if not p.exists():
            raise FileNotFoundError(f"no deployment manifest {p} (run scripts/setup_roles.py)")
        data = json.loads(p.read_text())
        if data["profile"] != profile:
            raise ValueError(f"{p} is for profile {data['profile']!r}, not {profile!r}")
        return cls(**data)

    def role_map(self) -> RoleMap:
        r = self.roles
        rm = RoleMap(a=r["A"], a2=r["A2"], b=r["B"], watchers=tuple(r["watchers"]), ss58_format=r.get("ss58_format", 42))
        if not (same(rm.m_mint, r["M_mint"]["address"]) and same(rm.m_admin, r["M_admin"]["address"])
                and same(rm.m_watch, r["M_watch"]["address"])):
            raise ValueError("manifest multisig addresses do not match their signatories")
        return rm
