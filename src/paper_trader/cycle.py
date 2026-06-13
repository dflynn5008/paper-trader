import logging
from collections.abc import Callable
from pathlib import Path

import pandas as pd
from alpaca.trading.client import TradingClient

from paper_trader.client import create_trading_client
from paper_trader.config import Settings
from paper_trader.executor import submit_market_order
from paper_trader.notifier import DiscordNotifier
from paper_trader.portfolio_state import PortfolioState
from paper_trader.risk import (
    compute_capital_snapshot,
    get_open_position,
    validate_trade,
)
from paper_trader.strategy import evaluate_sma_crossover
from paper_trader.strategy.sma_crossover import Signal
from paper_trader.strategy.wisdom import refine_with_wisdom

logger = logging.getLogger(__name__)


def run_trading_cycle(
    settings: Settings,
    notifier: DiscordNotifier,
    state: PortfolioState,
    fetch_bars: Callable[[Settings, str], pd.DataFrame],
) -> int:
    client = create_trading_client(settings)

    account = client.get_account()
    logger.info("Connected to Alpaca paper account: %s", account.account_number)
    if settings.market.value == "crypto" and account.crypto_status is None:
        logger.warning(
            "Crypto trading may not be enabled on this Alpaca account. "
            "Enable it in the Alpaca dashboard if orders fail."
        )

    logger.info(
        "%s virtual budget: $%.2f across %s",
        settings.market_label,
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
            f"**{settings.market_label} trading halted**\n"
            f"Virtual equity: ${snapshot.virtual_equity:.2f}\n"
            "Capital floor was hit earlier. No new trades will run."
        )
        return 0

    sells = []
    buys = []
    alerts = []

    for symbol in settings.symbols:
        bars = fetch_bars(settings, symbol)
        result = refine_with_wisdom(evaluate_sma_crossover(bars), bars)
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

    _execute_sells(client, settings, notifier, state, snapshot, sells, alerts)
    snapshot = compute_capital_snapshot(client, settings, state)
    _execute_buys(client, settings, notifier, state, snapshot, buys, alerts)

    snapshot = compute_capital_snapshot(client, settings, state)
    if state.halted:
        notifier.send(
            f"**{settings.market_label} trading halted**\n"
            f"Virtual equity: ${snapshot.virtual_equity:.2f}\n"
            "Capital floor reached. No more trades will be placed."
        )
    elif alerts:
        notifier.send(f"**{settings.market_label} signals / blocks**\n" + "\n".join(alerts))

    logger.info("Cycle complete. Virtual equity: $%.2f", snapshot.virtual_equity)
    return 0


def _execute_sells(
    client: TradingClient,
    settings: Settings,
    notifier: DiscordNotifier,
    state: PortfolioState,
    snapshot,
    sells,
    alerts,
) -> None:
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
            alerts.append(f"{symbol} SELL blocked: {reason}")
            continue

        try:
            position = get_open_position(client, symbol)
            sell_pnl = float(position.market_value) - float(position.cost_basis)
            qty = float(position.qty)
        except Exception:
            logger.info("%s SELL skipped: position no longer open", symbol)
            continue

        order_id = submit_market_order(
            client, settings, symbol, result.signal, qty=qty
        )
        state.realized_pnl += sell_pnl
        state.save()
        logger.info("Submitted SELL for %s units of %s (order_id=%s)", qty, symbol, order_id)
        snapshot = compute_capital_snapshot(client, settings, state)
        notifier.send(
            f"**Paper {settings.market_label} SELL: {symbol}**\n"
            f"Units: {qty}\n"
            f"Est. P&L: ${sell_pnl:+.2f}\n"
            f"Virtual equity: ${snapshot.virtual_equity:.2f}\n"
            f"Order: {order_id}"
        )


def _execute_buys(
    client: TradingClient,
    settings: Settings,
    notifier: DiscordNotifier,
    state: PortfolioState,
    snapshot,
    buys,
    alerts,
) -> None:
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
            settings,
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
            f"**Paper {settings.market_label} BUY: {symbol}**\n"
            f"Notional: ${settings.trade_notional_usd:.2f}\n"
            f"Virtual equity: ${snapshot.virtual_equity:.2f}\n"
            f"Order: {order_id}"
        )


def run_with_settings(
    settings: Settings,
    fetch_bars: Callable[[Settings, str], pd.DataFrame],
) -> int:
    notifier = DiscordNotifier(settings.discord_webhook_url)
    state = PortfolioState.load(
        settings.starting_capital,
        Path(settings.state_path),
    )

    try:
        return run_trading_cycle(settings, notifier, state, fetch_bars)
    except Exception as exc:
        logger.exception("%s trading cycle failed", settings.market_label)
        notifier.send(f"**{settings.market_label} trader error**\n{exc}")
        return 1
