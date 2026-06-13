"""Send the daily portfolio report to Discord."""

import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from paper_trader.logging_utils import setup_logging
from paper_trader.report import send_daily_report

logger = logging.getLogger(__name__)


def main() -> int:
    setup_logging()
    try:
        return send_daily_report(os.getenv("DISCORD_WEBHOOK_URL"))
    except Exception:
        logger.exception("Daily report failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
