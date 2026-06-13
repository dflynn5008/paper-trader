from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.trading.client import TradingClient

from paper_trader.config import Settings


def create_trading_client(settings: Settings) -> TradingClient:
    return TradingClient(
        api_key=settings.api_key,
        secret_key=settings.secret_key,
        paper=settings.paper,
    )


def create_data_client(settings: Settings) -> StockHistoricalDataClient:
    return StockHistoricalDataClient(
        api_key=settings.api_key,
        secret_key=settings.secret_key,
    )


def create_crypto_data_client(settings: Settings) -> CryptoHistoricalDataClient:
    return CryptoHistoricalDataClient(
        api_key=settings.api_key,
        secret_key=settings.secret_key,
    )