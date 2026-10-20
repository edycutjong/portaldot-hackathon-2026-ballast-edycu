"""Chain profiles: which chain Ballast is talking to, and what that chain's numbers are.

Ballast targets the Portaldot V3 testnet (profile `v3`, pinned at the 2026-10-20 day-0 check). The drills also run
on labelled stand-ins, and nothing measured on a stand-in is presented as V3. A chain is identified by its genesis hash
and the blake2-256 hash of its `:code`; a mismatch with the configured profile fails loudly.

Block counts are derived from the block time measured on the chain in use:
H (heartbeat) ~ 10 min, K = 3 x H (heartbeat freeze), W ~ 24 h (wind-down trigger), N = 2 (poll step).
The durations are Ballast's design parameters, not chain facts; only the block time is measured.
"""

from __future__ import annotations

import hashlib
import statistics
from dataclasses import dataclass, field

import xxhash

from .rpc import Rpc

UNVERIFIED = "UNVERIFIED (V3 day-0)"



def twox128(data: bytes) -> bytes:
    return xxhash.xxh64(data, seed=0).intdigest().to_bytes(8, "little") + xxhash.xxh64(
        data, seed=1
    ).intdigest().to_bytes(8, "little")


def storage_key(pallet: str, item: str) -> str:
    return "0x" + (twox128(pallet.encode()) + twox128(item.encode())).hex()


TIMESTAMP_NOW = storage_key("Timestamp", "Now")
CODE_KEY = "0x" + b":code".hex()

BLOCK_TIME_RESOLUTION_MS = 100  # +-1 ms timestamp jitter must not move H/K/W
HEARTBEAT_MS = 10 * 60 * 1000
WIND_DOWN_MS = 24 * 60 * 60 * 1000
POLL_EVERY_BLOCKS = 2
MIN_SAMPLE_BLOCKS = 20

# Multisig `as_multi` call shapes.
SHAPE_WEIGHT_V2 = "weight-v2"  # modern: max_weight = Weight { ref_time, proof_size }
SHAPE_LEGACY_1002 = "legacy-1002"  # spec 1002: call = OpaqueCall, store_call: bool, max_weight: u64


class ProfileError(RuntimeError):
    pass


class UnknownProfile(ProfileError):
    pass


class UnknownChain(ProfileError):
    pass


class ProfileMismatch(ProfileError):
    pass


class ProfileUnverified(ProfileError):
    pass


@dataclass(frozen=True)
class Profile:
    name: str
    label: str
    is_standin: bool
    default_url: str
    genesis_hash: str | None
    code_hash: str | None
    spec_name: str
    spec_version: int | None
    decimals: int | None
    multisig_shape: str | None
    type_registry_preset: str | None = None
    patch_assets_u64: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        return self.name


PROFILES: dict[str, Profile] = {
    # Pinned at Ballast's V3 day-0 check (2026-10-20, evidence/v3-day0-20261020T131224Z.json, re-checked in
    # evidence/v3-day0-20261020T152616Z.json): chain_getBlockHash(0),
    # blake2_256(:code), state_getRuntimeVersion, system_properties. The pre-launch guide said
    # portaldotV3/3000/tPOTv3 at testnetv3-node.feso-apps.xyz (retired); the live chain differs.
    "v3": Profile(
        name="v3",
        label="Portaldot V3 testnet",
        is_standin=False,
        default_url="wss://test-node-v3.portaldot.dev",
        genesis_hash="0xd4f9acbcf7f52388d8b095abe3c198d19fc510e0343e643e87cfbccb155283bd",
        code_hash="0xedc03c9dc81d39fea5c02893cc34cf2ec898d55d7ee8f8e89eb27597a724c7c2",
        spec_name="portaldot-v3",
        spec_version=3002,
        decimals=14,
        multisig_shape=SHAPE_WEIGHT_V2,  # as_multi(threshold, other_signatories, maybe_timepoint, call, max_weight: Weight)
        notes=("PortaldotV3 Test, node 3.0.0-dev-fddd43141f2, token tPOT, ss58 42",),
    ),
    "standin-upstream": Profile(
        name="standin-upstream",
        label="standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)",
        is_standin=True,
        default_url="ws://127.0.0.1:49944",
        genesis_hash="0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2",
        code_hash="0x72e84be232be151b059440f89710895de0cb6b71b6529f97e9c02340765f1ec0",
        spec_name="node",
        spec_version=268,
        decimals=12,
        multisig_shape=SHAPE_WEIGHT_V2,
        notes=("polkadot-stable2606-3 substrate-node 3.0.0-dev-9d0dc6e8fbb, aarch64-apple-darwin",),
    ),
    "standin-1002": Profile(
        name="standin-1002",
        label="standin-1002 (portaldot_dev 2.0.0 --dev, runtime spec 1002, NOT V3)",
        is_standin=True,
        default_url="ws://127.0.0.1:49944",
        genesis_hash="0x53c36c0fc46f5bb2429d701b5ad7a0577b343aa53c4964333f1922611974dd22",
        code_hash="0x8c0d4d9d638ad05e7d214e1496321cea00274698e4bcf5b2006c3eaf86b7fa80",
        spec_name="portaldot",
        spec_version=1002,
        decimals=None,  # system_properties is empty on this node
        multisig_shape=SHAPE_LEGACY_1002,
        type_registry_preset="legacy",
        patch_assets_u64=True,
        notes=("Assets Balance is u64 on spec 1002: calls and events are re-typed on connect",),
    ),
}


def get_profile(name: str) -> Profile:
    try:
        return PROFILES[name]
    except KeyError:
        raise UnknownProfile(f"unknown chain profile {name!r}; expected one of {', '.join(PROFILES)}") from None


@dataclass(frozen=True)
class BlockCounts:
    block_time_ms: float
    heartbeat_h: int
    heartbeat_freeze_k: int
    wind_down_w: int
    poll_n: int

    def as_dict(self) -> dict:
        return {
            "block_time_ms": self.block_time_ms,
            "H": self.heartbeat_h,
            "K": self.heartbeat_freeze_k,
            "W": self.wind_down_w,
            "N": self.poll_n,
        }


def derive_block_counts(block_time_ms: float) -> BlockCounts:
    """H ~ 10 min, K = 3H, W ~ 24 h, N = 2 — all in blocks of the measured length."""
    if block_time_ms <= 0:
        raise ValueError("block time must be positive")
    h = max(1, round(HEARTBEAT_MS / block_time_ms))
    return BlockCounts(
        block_time_ms=block_time_ms,
        heartbeat_h=h,
        heartbeat_freeze_k=3 * h,
        wind_down_w=max(1, round(WIND_DOWN_MS / block_time_ms)),
        poll_n=POLL_EVERY_BLOCKS,
    )


def round_block_time(ms: float) -> float:
    return max(BLOCK_TIME_RESOLUTION_MS, round(ms / BLOCK_TIME_RESOLUTION_MS) * BLOCK_TIME_RESOLUTION_MS)


@dataclass(frozen=True)
class ChainFacts:
    """What a node says about itself. Gathered by `observe`, judged by `classify`."""

    genesis_hash: str
    code_hash: str
    spec_name: str
    spec_version: int
    token_decimals: int | None
    head: int
    block_time_ms: float | None = None  # median of per-block deltas
    mean_block_time_ms: float | None = None
    sample_blocks: int = 0


@dataclass(frozen=True)
class ChainIdentity:
    profile: Profile
    facts: ChainFacts
    counts: BlockCounts | None
    notes: tuple[str, ...]

    @property
    def decimals(self) -> int | None:
        """Reported by the node; a pinned value is a fallback on stand-ins only, never on V3."""
        if self.facts.token_decimals is not None:
            return self.facts.token_decimals
        return self.profile.decimals if self.profile.is_standin else None

    def banner(self) -> str:
        if self.profile.is_standin:
            tag = "STAND-IN, NOT V3"
        elif self.profile.genesis_hash is None:
            tag = f"V3 by spec name only, genesis not pinned: {UNVERIFIED}"
        else:
            tag = "V3"
        return (
            f"[{self.profile.name} | {tag}] genesis {self.facts.genesis_hash[:10]}… "
            f"spec {self.facts.spec_name}/{self.facts.spec_version} head #{self.facts.head}"
        )

    def as_dict(self) -> dict:
        return {
            "profile": self.profile.name,
            "label": self.profile.label,
            "is_standin": self.profile.is_standin,
            "genesis_pinned": self.profile.genesis_hash is not None,
            "genesis_hash": self.facts.genesis_hash,
            "code_hash": self.facts.code_hash,
            "spec_name": self.facts.spec_name,
            "spec_version": self.facts.spec_version,
            "token_decimals": self.facts.token_decimals,
            "decimals_source": "system_properties" if self.facts.token_decimals is not None else "unreported",
            "head": self.facts.head,
            "multisig_shape": self.profile.multisig_shape or UNVERIFIED,
            "block_counts": (
                {
                    **self.counts.as_dict(),
                    "block_time_basis": f"median of per-block timestamp deltas, rounded to {BLOCK_TIME_RESOLUTION_MS} ms",
                    "median_block_time_ms": self.facts.block_time_ms,
                    "mean_block_time_ms": self.facts.mean_block_time_ms,
                    "measured_over_blocks": self.facts.sample_blocks,
                }
                if self.counts
                else ("not measured" if self.profile.is_standin else UNVERIFIED)
            ),
            "notes": list(self.notes),
        }


def blake2_256(data: bytes) -> str:
    return "0x" + hashlib.blake2b(data, digest_size=32).hexdigest()


def _hex_to_bytes(value: str) -> bytes:
    return bytes.fromhex(value[2:] if value.startswith("0x") else value)


def read_timestamp_ms(rpc: Rpc, block_hash: str) -> int:
    raw = rpc.call("state_getStorage", [TIMESTAMP_NOW, block_hash])
    if raw is None:
        raise ProfileError(f"no Timestamp.Now at {block_hash}")
    return int.from_bytes(_hex_to_bytes(raw), "little")


def measure_block_time(rpc: Rpc, head: int, sample_blocks: int = MIN_SAMPLE_BLOCKS) -> tuple[float, float, int]:
    """(mean ms, median ms, blocks sampled) over the last `sample_blocks` blocks.

    Block counts are derived from the median: a stand-in that was stopped and restarted leaves one long gap
    that inflates the mean, while the median stays the chain's production cadence. Both are reported.
    """
    if sample_blocks < MIN_SAMPLE_BLOCKS:
        raise ValueError(f"sample at least {MIN_SAMPLE_BLOCKS} blocks")
    if head < sample_blocks + 1:
        raise ProfileError(f"head #{head} too low to sample {sample_blocks} blocks (block #1 has the genesis slot)")
    stamps = [
        read_timestamp_ms(rpc, rpc.call("chain_getBlockHash", [n])) for n in range(head - sample_blocks, head + 1)
    ]
    deltas = [b - a for a, b in zip(stamps, stamps[1:])]
    return (stamps[-1] - stamps[0]) / sample_blocks, float(statistics.median(deltas)), sample_blocks


def observe(rpc: Rpc, *, measure: bool = True, sample_blocks: int = MIN_SAMPLE_BLOCKS) -> ChainFacts:
    genesis = rpc.call("chain_getBlockHash", [0])
    code = rpc.call("state_getStorage", [CODE_KEY])
    if code is None:
        raise ProfileError("node returned no :code")
    version = rpc.call("state_getRuntimeVersion")
    props = rpc.call("system_properties") or {}
    head = int(rpc.call("chain_getHeader")["number"], 16)
    decimals = props.get("tokenDecimals")
    if isinstance(decimals, list):
        decimals = decimals[0] if decimals else None
    mean, median, sampled = (None, None, 0)
    if measure:
        mean, median, sampled = measure_block_time(rpc, head, sample_blocks)
    return ChainFacts(
        genesis_hash=genesis,
        code_hash=blake2_256(_hex_to_bytes(code)),
        spec_name=version["specName"],
        spec_version=int(version["specVersion"]),
        token_decimals=decimals,
        head=head,
        block_time_ms=median,
        mean_block_time_ms=mean,
        sample_blocks=sampled,
    )


def match_profile(facts: ChainFacts) -> Profile | None:
    """The profile whose pinned genesis hash (or, for unpinned V3, spec name) matches the chain."""
    for profile in PROFILES.values():
        if profile.genesis_hash and profile.genesis_hash == facts.genesis_hash:
            return profile
    for profile in PROFILES.values():
        if profile.genesis_hash is None and profile.spec_name == facts.spec_name:
            return profile
    return None


def classify(facts: ChainFacts, profile_name: str) -> ChainIdentity:
    profile = get_profile(profile_name)
    seen = match_profile(facts)
    if seen is None:
        raise UnknownChain(
            f"unknown chain: genesis {facts.genesis_hash}, spec {facts.spec_name}/{facts.spec_version} "
            f"matches no profile (configured: {profile.name})"
        )
    if seen.name != profile.name:
        raise ProfileMismatch(f"profile mismatch: the configured profile is {profile.name!r}, the node is {seen.name!r}")
    notes = list(profile.notes)
    if profile.code_hash and profile.code_hash != facts.code_hash:
        raise ProfileMismatch(
            f"{profile.name}: runtime :code hash {facts.code_hash} != pinned {profile.code_hash} "
            "(different binary or runtime upgrade)"
        )
    if profile.code_hash is None:
        notes.append(f":code hash {facts.code_hash} observed, not pinned ({UNVERIFIED})")
    if profile.spec_version is not None and facts.spec_version != profile.spec_version:
        msg = f"spec_version {facts.spec_version} != expected {profile.spec_version}"
        if profile.is_standin:
            raise ProfileMismatch(f"{profile.name}: {msg}")
        notes.append(msg)
    if facts.token_decimals is not None and profile.decimals is not None and facts.token_decimals != profile.decimals:
        raise ProfileMismatch(f"{profile.name}: tokenDecimals {facts.token_decimals} != expected {profile.decimals}")
    counts = derive_block_counts(round_block_time(facts.block_time_ms)) if facts.block_time_ms else None
    if counts and profile.is_standin:
        notes.append(f"H/K/W/N derived from the {profile.name} block time measured over {facts.sample_blocks} blocks")
    return ChainIdentity(profile=profile, facts=facts, counts=counts, notes=tuple(notes))


def identify(rpc: Rpc, profile_name: str, *, measure: bool = True, sample_blocks: int = MIN_SAMPLE_BLOCKS) -> ChainIdentity:
    return classify(observe(rpc, measure=measure, sample_blocks=sample_blocks), profile_name)


def require_standin(profile: Profile, what: str = "deterministic dev keys") -> None:
    """Dev URIs (//Alice, //BallastA, ...) are public. They are refused on anything but a stand-in."""
    if not profile.is_standin:
        raise ProfileError(f"refusing {what} on profile {profile.name!r}: dev keys are allowed on stand-ins only")


def require_multisig_shape(profile: Profile) -> str:
    if profile.multisig_shape is None:
        raise ProfileUnverified(f"{profile.name}: as_multi call shape is {UNVERIFIED}")
    return profile.multisig_shape
