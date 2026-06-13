from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, QueryOrderStatus, TimeInForce
from alpaca.trading.requests import GetOrdersRequest, MarketOrderRequest

from paper_trader.config import MarketKind, Settings
from paper_trader.strategy.sma_crossover import Signal


def submit_market_order(
    client: TradingClient,
    settings: Settings,
    symbol: str,
    signal: Signal,
    *,
    qty: float | None = None,
    notional: float | None = None,
) -> str:
    side = OrderSide.BUY if signal == Signal.BUY else OrderSide.SELL
    time_in_force = (
        TimeInForce.GTC if settings.market == MarketKind.CRYPTO else TimeInForce.DAY
    )
    order = MarketOrderRequest(
        symbol=symbol,
        side=side,
        time_in_force=time_in_force,
        qty=qty,
        notional=notional,
    )
    submitted = client.submit_order(order)
    return str(submitted.id)
