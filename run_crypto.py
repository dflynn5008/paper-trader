"""Run one crypto paper-trading evaluation cycle (24/7 markets)."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from paper_trader.config import load_crypto_settings
from paper_trader.cycle import run_with_settings
from paper_trader.data import fetch_crypto_hourly_bars
from paper_trader.logging_utils import setup_logging

logger = logging.getLogger(__name__)


def main() -> int:
    setup_logging()
    return run_with_settings(load_crypto_settings(), fetch_crypto_hourly_bars)


if __name__ == "__main__":
    raise SystemExit(main())
