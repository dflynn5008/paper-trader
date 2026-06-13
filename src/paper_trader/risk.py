from dataclasses import dataclass

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from paper_trader.config import Settings
from paper_trader.portfolio_state import PortfolioState
from paper_trader.strategy.sma_crossover import Signal


@dataclass(frozen=True)
class CapitalSnapshot:
    virtual_equity: float
    open_positions: int
    unrealized_pnl: float
    cash_remaining: float


def get_watchlist_positions(client: TradingClient, symbols: tuple[str, ...]):
    positions = client.get_all_positions()
    watchlist = set(symbols)
    return [position for position in positions if position.symbol in watchlist]


def get_open_position_qty(client: TradingClient, symbol: str) -> int:
    try:
        position = client.get_open_position(symbol)
        return int(float(position.qty))
    except Exception:
        return 0


def count_todays_orders(client: TradingClient) -> int:
    orders = client.get_orders(
        filter=GetOrdersRequest(status=QueryOrderStatus.ALL, limit=100)
    )
    today = client.get_clock().timestamp.date()
    return sum(1 for order in orders if order.submitted_at.date() == today)


def compute_capital_snapshot(
    client: TradingClient,
    settings: Settings,
    state: PortfolioState,
) -> CapitalSnapshot:
    positions = get_watchlist_positions(client, settings.symbols)
    position_value = sum(float(position.market_value) for position in positions)
    cost_basis = sum(float(position.cost_basis) for position in positions)
    unrealized_pnl = position_value - cost_basis
    virtual_equity = settings.starting_capital + state.realized_pnl + unrealized_pnl
    cash_remaining = virtual_equity - position_value

    return CapitalSnapshot(
        virtual_equity=virtual_equity,
        open_positions=len(positions),
        unrealized_pnl=unrealized_pnl,
        cash_remaining=cash_remaining,
    )


def check_capital_guard(
    snapshot: CapitalSnapshot,
    state: PortfolioState,
) -> tuple[bool, str]:
    if state.halted:
        return False, "Trading halted after capital floor was hit"

    if snapshot.virtual_equity <= 0:
        state.halted = True
        state.save()
        return False, "Capital floor reached (virtual equity <= $0); trading halted"

    return True, f"Virtual equity ${snapshot.virtual_equity:.2f}"


def validate_trade(
    client: TradingClient,
    settings: Settings,
    state: PortfolioState,
    snapshot: CapitalSnapshot,
    symbol: str,
    signal: Signal,
) -> tuple[bool, str]:
    if signal == Signal.HOLD:
        return False, "Strategy returned HOLD"

    capital_ok, capital_reason = check_capital_guard(snapshot, state)
    if not capital_ok:
        return False, capital_reason

    position_qty = get_open_position_qty(client, symbol)
    todays_orders = count_todays_orders(client)

    if todays_orders >= settings.max_daily_orders:
        return False, f"Daily order limit reached ({settings.max_daily_orders})"

    if signal == Signal.BUY:
        if position_qty > 0:
            return False, "Already long; skipping duplicate BUY"
        if snapshot.open_positions >= settings.max_positions:
            return False, f"Max positions reached ({settings.max_positions})"
        if snapshot.cash_remaining < settings.trade_notional_usd:
            return (
                False,
                f"Insufficient virtual cash (${snapshot.cash_remaining:.2f} remaining)",
            )
        return True, (
            f"Approved BUY ${settings.trade_notional_usd:.2f} notional "
            f"({capital_reason})"
        )

    if signal == Signal.SELL:
        if position_qty <= 0:
            return False, "No open position to sell"
        return True, f"Approved SELL of {position_qty} shares"

    return False, f"Unsupported signal: {signal}"
