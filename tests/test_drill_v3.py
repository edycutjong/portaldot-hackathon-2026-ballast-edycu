"""`ballast drill` on v3: scratch assets stay clear of the role-split assets, and the frozen-transfer error is pinned."""

from ballast.drill import DRILL_ASSET_FROM, FROZEN_TRANSFER_ERRORS, V3_DRILL_ASSET_FROM


def test_v3_scratch_assets_start_above_the_role_split_assets():
    assert V3_DRILL_ASSET_FROM > 4402  # deployments/v3.json: breaker 4401, control 4402
    assert V3_DRILL_ASSET_FROM != DRILL_ASSET_FROM


def test_v3_frozen_transfer_error_is_pinned():
    assert FROZEN_TRANSFER_ERRORS["v3"] == "Err(Assets.AssetNotLive)"
