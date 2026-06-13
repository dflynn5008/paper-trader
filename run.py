"""Run one paper-trading evaluation cycle."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from paper_trader.client import create_trading_client
from paper_trader.config import load_settings
from paper_trader.data import fetch_daily_bars
from paper_trader.executor import submit_market_order
from paper_trader.logging_utils import setup_logging
from paper_trader.notifier import DiscordNotifier
from paper_trader.portfolio_state import PortfolioState
from paper_trader.risk import (
    compute_capital_snapshot,
    validate_trade,
)
from paper_trader.strategy import evaluate_sma_crossover
from paper_trader.strategy.sma_crossover import Signal

logger = logging.getLogger(__name__)


def main() -> int:
    setup_logging()
    settings = load_settings()
    notifier = DiscordNotifier(settings.discord_webhook_url)
    state = PortfolioState.load(settings.starting_capital)

    try:
        return _run_cycle(settings, notifier, state)
    except Exception as exc:
        logger.exception("Trading cycle failed")
        notifier.send(f"**Paper Trader error**\n{exc}")
        return 1


def _run_cycle(
    settings,
    notifier: DiscordNotifier,
    state: PortfolioState,
) -> int:
    client = create_trading_client(settings)

    account = client.get_account()
    logger.info("Connected to Alpaca paper account: %s", account.account_number)
    logger.info(
        "Virtual portfolio budget: $%.2f across %s",
        settings.starting_capital,
        ", ".join(settings.symbols),
    )

    snapshot = compute_capital_snapshot(client, settings, state)
    logger.info(
        "Virtual equity: $%.2f | cash remaining: $%.2f | open positions: %s",
        snapshot.virtual_equity,
        snapshot.cash_remaining,
        snapshot.open_positions,
    )

    if state.halted:
        notifier.send(
            "**Trading halted**\n"
            f"Virtual equity: ${snapshot.virtual_equity:.2f}\n"
            "Capital floor was hit earlier. No new trades will run."
        )
        return 0

    sells = []
    buys = []
    alerts = []

    for symbol in settings.symbols:
        bars = fetch_daily_bars(settings, symbol)
        result = evaluate_sma_crossover(bars)
        logger.info(
            "%s | %s | fast=%.2f slow=%.2f | %s",
            symbol,
            result.signal.value,
            result.fast_sma,
            result.slow_sma,
            result.reason,
        )

        if result.signal != Signal.HOLD and settings.discord_alert_signals:
            alerts.append(f"{symbol}: {result.signal.value.upper()} — {result.reason}")

        if result.signal == Signal.SELL:
            sells.append((symbol, result))
        elif result.signal == Signal.BUY:
            buys.append((symbol, result))

    for symbol, result in sells:
        approved, reason = validate_trade(
            client, settings, state, snapshot, symbol, result.signal
        )
        logger.info(
            "%s SELL risk check: %s (%s)",
            symbol,
            "approved" if approved else "blocked",
            reason,
        )
        if not approved:
            if result.signal == Signal.SELL:
                alerts.append(f"{symbol} SELL blocked: {reason}")
            continue

        try:
            position = client.get_open_position(symbol)
            sell_pnl = float(position.market_value) - float(position.cost_basis)
            qty = int(float(position.qty))
        except Exception:
            logger.info("%s SELL skipped: position no longer open", symbol)
            continue

        order_id = submit_market_order(client, symbol, result.signal, qty=qty)
        state.realized_pnl += sell_pnl
        state.save()
        logger.info("Submitted SELL for %s shares of %s (order_id=%s)", qty, symbol, order_id)
        snapshot = compute_capital_snapshot(client, settings, state)
        notifier.send(
            f"**Paper SELL: {symbol}**\n"
            f"Shares: {qty}\n"
            f"Est. P&L: ${sell_pnl:+.2f}\n"
            f"Virtual equity: ${snapshot.virtual_equity:.2f}\n"
            f"Order: {order_id}"
        )

    for symbol, result in buys:
        approved, reason = validate_trade(
            client, settings, state, snapshot, symbol, result.signal
        )
        logger.info(
            "%s BUY risk check: %s (%s)",
            symbol,
            "approved" if approved else "blocked",
            reason,
        )
        if not approved:
            alerts.append(f"{symbol} BUY blocked: {reason}")
            continue

        order_id = submit_market_order(
            client,
            symbol,
            result.signal,
            notional=settings.trade_notional_usd,
        )
        logger.info(
            "Submitted BUY for $%.2f notional of %s (order_id=%s)",
            settings.trade_notional_usd,
            symbol,
            order_id,
        )
        snapshot = compute_capital_snapshot(client, settings, state)
        notifier.send(
            f"**Paper BUY: {symbol}**\n"
            f"Notional: ${settings.trade_notional_usd:.2f}\n"
            f"Virtual equity: ${snapshot.virtual_equity:.2f}\n"
            f"Order: {order_id}"
        )

    if state.halted:
        notifier.send(
            "**Trading halted**\n"
            f"Virtual equity: ${snapshot.virtual_equity:.2f}\n"
            "Capital floor reached. No more trades will be placed."
        )
    elif alerts:
        notifier.send("**Signals / blocks**\n" + "\n".join(alerts))

    logger.info("Cycle complete. Virtual equity: $%.2f", snapshot.virtual_equity)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
