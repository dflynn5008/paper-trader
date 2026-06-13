import os
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

from paper_trader.paths import CRYPTO_STATE_PATH, STOCK_STATE_PATH

load_dotenv()


class MarketKind(str, Enum):
    STOCKS = "stocks"
    CRYPTO = "crypto"


@dataclass(frozen=True)
class Settings:
    market: MarketKind
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
    state_path: str

    @property
    def market_label(self) -> str:
        return "Stocks" if self.market == MarketKind.STOCKS else "Crypto"


def _parse_symbols(raw: str, label: str) -> tuple[str, ...]:
    symbols = tuple(
        sorted({symbol.strip().upper() for symbol in raw.split(",") if symbol.strip()})
    )
    if not symbols:
        raise ValueError(f"{label} must list at least one symbol")
    return symbols


def _load_common(market: MarketKind) -> Settings:
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

    if market == MarketKind.STOCKS:
        symbols = _parse_symbols(
            os.getenv("SYMBOLS", "F,SOFI,PLTR,AMD,QQQ"),
            "SYMBOLS",
        )
        starting_capital = float(os.getenv("STARTING_CAPITAL", "100"))
        trade_notional = float(os.getenv("TRADE_NOTIONAL_USD", "25"))
        max_positions = int(os.getenv("MAX_POSITIONS", "2"))
        max_daily_orders = int(os.getenv("MAX_DAILY_ORDERS", "3"))
        state_path = str(STOCK_STATE_PATH)
    else:
        symbols = _parse_symbols(
            os.getenv("CRYPTO_SYMBOLS", "BTC/USD,ETH/USD,SOL/USD"),
            "CRYPTO_SYMBOLS",
        )
        starting_capital = float(os.getenv("CRYPTO_STARTING_CAPITAL", "100"))
        trade_notional = float(os.getenv("CRYPTO_TRADE_NOTIONAL_USD", "25"))
        max_positions = int(os.getenv("CRYPTO_MAX_POSITIONS", "2"))
        max_daily_orders = int(os.getenv("CRYPTO_MAX_DAILY_ORDERS", "6"))
        state_path = str(CRYPTO_STATE_PATH)

    if starting_capital <= 0:
        raise ValueError("Starting capital must be greater than 0")
    if trade_notional <= 0:
        raise ValueError("Trade notional must be greater than 0")
    if trade_notional > starting_capital:
        raise ValueError("Trade notional cannot exceed starting capital")

    return Settings(
        market=market,
        api_key=api_key,
        secret_key=secret_key,
        paper=paper,
        symbols=symbols,
        starting_capital=starting_capital,
        trade_notional_usd=trade_notional,
        max_positions=max_positions,
        max_daily_orders=max_daily_orders,
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", "").strip() or None,
        discord_alert_signals=os.getenv("DISCORD_ALERT_SIGNALS", "false").strip().lower()
        in {"1", "true", "yes", "on"},
        state_path=state_path,
    )


def load_settings() -> Settings:
    return _load_common(MarketKind.STOCKS)


def load_crypto_settings() -> Settings:
    return _load_common(MarketKind.CRYPTO)
