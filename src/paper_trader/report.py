import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from alpaca.trading.client import TradingClient

from paper_trader.client import create_trading_client
from paper_trader.config import Settings, load_crypto_settings, load_settings
from paper_trader.data import fetch_crypto_hourly_bars, fetch_daily_bars
from paper_trader.notifier import DiscordNotifier
from paper_trader.portfolio_state import PortfolioState
from paper_trader.risk import compute_capital_snapshot, get_watchlist_positions
from paper_trader.strategy.sma_crossover import Signal
from paper_trader.strategy.wisdom import refine_with_wisdom
from paper_trader.strategy import evaluate_sma_crossover

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MarketReport:
    label: str
    starting_capital: float
    virtual_equity: float
    cash_remaining: float
    realized_pnl: float
    unrealized_pnl: float
    open_positions: int
    halted: bool
    position_lines: tuple[str, ...]
    signal_lines: tuple[str, ...]


def _pct_change(current: float, start: float) -> float:
    if start == 0:
        return 0.0
    return ((current - start) / start) * 100


def _build_market_report(
    client: TradingClient,
    settings: Settings,
    fetch_bars,
) -> MarketReport:
    state = PortfolioState.load(
        settings.starting_capital,
        Path(settings.state_path),
    )
    snapshot = compute_capital_snapshot(client, settings, state)
    positions = get_watchlist_positions(client, settings.symbols)

    position_lines = tuple(
        f"{pos.symbol}: ${float(pos.market_value):.2f} "
        f"({float(pos.unrealized_pl):+.2f})"
        for pos in positions
    ) or ("None",)

    signal_lines = []
    for symbol in settings.symbols:
        bars = fetch_bars(settings, symbol)
        result = refine_with_wisdom(evaluate_sma_crossover(bars), bars)
        if result.signal == Signal.HOLD:
            signal_lines.append(f"{symbol}: HOLD")
        else:
            signal_lines.append(
                f"{symbol}: {result.signal.value.upper()} — {result.reason}"
            )

    return MarketReport(
        label=settings.market_label,
        starting_capital=settings.starting_capital,
        virtual_equity=snapshot.virtual_equity,
        cash_remaining=snapshot.cash_remaining,
        realized_pnl=state.realized_pnl,
        unrealized_pnl=snapshot.unrealized_pnl,
        open_positions=snapshot.open_positions,
        halted=state.halted,
        position_lines=position_lines,
        signal_lines=tuple(signal_lines),
    )


def _format_market_section(report: MarketReport) -> str:
    change = _pct_change(report.virtual_equity, report.starting_capital)
    status = "HALTED" if report.halted else "Active"
    positions = "\n".join(f"  • {line}" for line in report.position_lines)
    signals = "\n".join(f"  • {line}" for line in report.signal_lines)

    return (
        f"**{report.label}** ({status})\n"
        f"Equity: **${report.virtual_equity:.2f}** ({change:+.1f}% vs start)\n"
        f"Cash: ${report.cash_remaining:.2f} | "
        f"Realized: ${report.realized_pnl:+.2f} | "
        f"Unrealized: ${report.unrealized_pnl:+.2f}\n"
        f"Positions ({report.open_positions}):\n{positions}\n"
        f"Signals:\n{signals}"
    )


def build_daily_report(client: TradingClient) -> str:
    stock_settings = load_settings()
    crypto_settings = load_crypto_settings()

    stock = _build_market_report(client, stock_settings, fetch_daily_bars)
    crypto = _build_market_report(client, crypto_settings, fetch_crypto_hourly_bars)

    combined_start = stock.starting_capital + crypto.starting_capital
    combined_equity = stock.virtual_equity + crypto.virtual_equity
    combined_change = _pct_change(combined_equity, combined_start)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"📊 **Paper Trader Daily Report**\n"
        f"{now}\n\n"
        f"**Combined virtual equity: ${combined_equity:.2f}** "
        f"({combined_change:+.1f}% vs ${combined_start:.0f} start)\n\n"
        f"{_format_market_section(stock)}\n\n"
        f"{_format_market_section(crypto)}\n\n"
        "_Trades only fire on strategy signals with risk guards. "
        "This is paper money — not financial advice._"
    )


def send_daily_report(webhook_url: str | None) -> int:
    notifier = DiscordNotifier(webhook_url)
    if not notifier.enabled:
        logger.error("DISCORD_WEBHOOK_URL is required for daily reports")
        return 1

    client = create_trading_client(load_settings())
    message = build_daily_report(client)
    notifier.send(message)
    logger.info("Daily report sent to Discord")
    return 0
