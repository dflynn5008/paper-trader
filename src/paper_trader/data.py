from datetime import datetime, timedelta, timezone

import pandas as pd
from alpaca.data.enums import DataFeed
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from paper_trader.client import create_crypto_data_client, create_data_client
from paper_trader.config import Settings


def fetch_daily_bars(settings: Settings, symbol: str, days: int = 60) -> pd.DataFrame:
    client = create_data_client(settings)
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed.IEX,
    )
    bars = client.get_stock_bars(request).df

    if bars.empty:
        raise ValueError(f"No bar data returned for {symbol}")

    if isinstance(bars.index, pd.MultiIndex):
        bars = bars.xs(symbol, level="symbol")

    return bars.sort_index()


def fetch_crypto_hourly_bars(
    settings: Settings,
    symbol: str,
    hours: int = 120,
) -> pd.DataFrame:
    client = create_crypto_data_client(settings)
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    request = CryptoBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Hour,
        start=start,
        end=end,
    )
    bars = client.get_crypto_bars(request).df

    if bars.empty:
        raise ValueError(f"No crypto bar data returned for {symbol}")

    if isinstance(bars.index, pd.MultiIndex):
        bars = bars.xs(symbol, level="symbol")

    return bars.sort_index()