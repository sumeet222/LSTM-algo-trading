"""V4 exact accountant with V5 policy identity included in each hash-chain event."""

from ..final_backtest_v4.book import Account as FrozenAccount
from ..final_backtest_v4.book import Lot, Order, Request
from .protocol import POLICY


class Account(FrozenAccount):
    def record(self, kind: str, at: int, **fields) -> None:
        super().record(kind, at, V5_POLICY_VARIANT=POLICY, **fields)


__all__ = ["Account", "Lot", "Order", "Request"]
