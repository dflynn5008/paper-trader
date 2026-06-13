import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_key: str
    secret_key: str
    paper: bool
    symbols: tuple[str, ...]
    starting_capital: float
    trade_notional_usd: float
    max_positions: int
    max_daily_orders: int
    discord_webhook_url: str | None
    discord_alert_signals: bool


def _parse_symbols(raw: str) -> tuple[str, ...]:
    symbols = tuple(
        sorted({symbol.strip().upper() for symbol in raw.split(",") if symbol.strip()})
    )
    if not symbols:
        raise ValueError("SYMBOLS must list at least one ticker, e.g. F,SOFI,PLTR")
    return symbols


def load_settings() -> Settings:
    api_key = os.getenv("ALPACA_API_KEY", "").strip()
    secret_key = os.getenv("ALPACA_SECRET_KEY", "").strip()

    if not api_key or not secret_key:
        raise ValueError(
            "Missing ALPACA_API_KEY or ALPACA_SECRET_KEY. "
            "Copy .env.example to .env and add your paper keys."
        )

    paper = os.getenv("ALPACA_PAPER", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if not paper:
        raise ValueError(
            "ALPACA_PAPER must be true for this project. "
            "Live trading is intentionally disabled in the scaffold."
        )

    starting_capital = float(os.getenv("STARTING_CAPITAL", "100"))
    trade_notional = float(os.getenv("TRADE_NOTIONAL_USD", "25"))

    if starting_capital <= 0:
        raise ValueError("STARTING_CAPITAL must be greater than 0")
    if trade_notional <= 0:
        raise ValueError("TRADE_NOTIONAL_USD must be greater than 0")
    if trade_notional > starting_capital:
        raise ValueError("TRADE_NOTIONAL_USD cannot exceed STARTING_CAPITAL")

    return Settings(
        api_key=api_key,
        secret_key=secret_key,
        paper=paper,
        symbols=_parse_symbols(os.getenv("SYMBOLS", "F,SOFI,PLTR,AMD,QQQ")),
        starting_capital=starting_capital,
        trade_notional_usd=trade_notional,
        max_positions=int(os.getenv("MAX_POSITIONS", "2")),
        max_daily_orders=int(os.getenv("MAX_DAILY_ORDERS", "3")),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", "").strip() or None,
        discord_alert_signals=os.getenv("DISCORD_ALERT_SIGNALS", "false").strip().lower()
        in {"1", "true", "yes", "on"},
    )
