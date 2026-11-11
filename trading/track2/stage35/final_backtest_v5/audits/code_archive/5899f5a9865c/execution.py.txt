"""Pure standing-order disposition; no price or future volume is an input."""

from ..final_backtest_v4.book import Order


def disposition(order: Order, start: int, received: int, lag: int, valid_bar: bool) -> str:
    if not order.decision < start or start < order.effective:
        raise ValueError("V5_ORDER_MUST_STAND_BEFORE_BAR")
    if received < start + 1 + lag:
        raise ValueError("V5_BAR_NOT_COMPLETED_AND_RECEIVED")
    if order.prior_volume_available > order.decision:
        raise ValueError("V5_FUTURE_VOLUME_CAPACITY")
    if order.expiry is not None and start > order.expiry:
        return "EXPIRE"
    return "EXECUTE" if valid_bar else "WAIT"
