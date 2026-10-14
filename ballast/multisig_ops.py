"""Multisig operations on chain: propose (first approval), execute (last approval), cancel, read a pending op.

pallet-multisig keeps only the call HASH on chain; every signer recomposes the call itself and the hash must match.
The first signer's `as_multi` (no timepoint) opens the operation and reserves its deposit; the last signer passes the
operation's timepoint and a `max_weight` covering the inner call, and the call dispatches inside the same extrinsic.
`Multisig.MultisigExecuted` is emitted even when the inner call fails — every receipt carries the inner result (I9).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .chain import Receipt, submit
from .chain_profile import Profile, require_multisig_shape
from .multisig import as_multi_params, multi_address, other_signatories, public_key


def call_hash(call: Any) -> str:
    return "0x" + call.call_hash.hex()


def call_weight(substrate: Any, call: Any, keypair: Any) -> dict:
    """Weight of the inner call from the node's payment API — the last signer's `max_weight`."""
    info = substrate.get_payment_info(call=call, keypair=keypair)
    w = info["weight"]
    if isinstance(w, int):  # weight v1 (spec 1002)
        return {"ref_time": w, "proof_size": 0}
    return {"ref_time": int(w["ref_time"]), "proof_size": int(w["proof_size"])}


@dataclass(frozen=True)
class Pending:
    multisig: str
    call_hash: str
    timepoint: dict  # {"height": int, "index": int}
    depositor: str
    approvals: tuple[str, ...]

    def approved_by(self, who: str) -> bool:
        return any(public_key(a) == public_key(who) for a in self.approvals)


def pending(substrate: Any, multisig: str, hash_: str, block_hash: str | None = None) -> Pending | None:
    value = substrate.query("Multisig", "Multisigs", [multisig, hash_], block_hash=block_hash).value
    if not value:
        return None
    return Pending(multisig=multisig, call_hash=hash_, timepoint=dict(value["when"]), depositor=value["depositor"],
                   approvals=tuple(value["approvals"]))


@dataclass
class MultisigAccount:
    signatories: list[str]
    threshold: int
    ss58_format: int = 42

    @property
    def address(self) -> str:
        return multi_address(self.signatories, self.threshold, ss58_format=self.ss58_format)

    def others(self, me: str) -> list[str]:
        return other_signatories(self.signatories, me, ss58_format=self.ss58_format)

    def propose(self, substrate: Any, profile: Profile, keypair: Any, call: Any, *, step: str, label: str) -> Receipt:
        """First approval: opens the operation (NewMultisig) and reserves the proposer's deposit."""
        if self.threshold < 2:
            raise ValueError("propose is for threshold >= 2 (1-of-N uses as_multi_threshold_1)")
        params = as_multi_params(require_multisig_shape(profile), threshold=self.threshold,
                                 other_signatories=self.others(keypair.ss58_address), maybe_timepoint=None, call=call,
                                 max_weight={"ref_time": 0, "proof_size": 0}, store_call=False)
        return submit(substrate, profile, keypair, "Multisig", "as_multi", params, step=step,
                      call_label=f"Multisig.as_multi({label}) — first approval")

    def execute(self, substrate: Any, profile: Profile, keypair: Any, call: Any, op: Pending, *, step: str,
                label: str) -> Receipt:
        """Last approval: dispatches the call. The receipt's `inner` holds the call's own result (I9)."""
        weight = call_weight(substrate, call, keypair)
        params = as_multi_params(require_multisig_shape(profile), threshold=self.threshold,
                                 other_signatories=self.others(keypair.ss58_address), maybe_timepoint=op.timepoint,
                                 call=call, max_weight=weight, store_call=False)
        return submit(substrate, profile, keypair, "Multisig", "as_multi", params, step=step,
                      call_label=f"Multisig.as_multi({label}) — final approval")

    def cancel(self, substrate: Any, profile: Profile, keypair: Any, op: Pending, *, step: str, label: str) -> Receipt:
        """Only the depositor can cancel; the deposit is returned (MultisigCancelled)."""
        params = {"threshold": self.threshold, "other_signatories": self.others(keypair.ss58_address),
                  "timepoint": op.timepoint, "call_hash": op.call_hash}
        return submit(substrate, profile, keypair, "Multisig", "cancel_as_multi", params, step=step,
                      call_label=f"Multisig.cancel_as_multi({label})")
