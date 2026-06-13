"""Send a test message to your Discord webhook."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from paper_trader.config import load_settings
from paper_trader.notifier import DiscordNotifier


def main() -> int:
    settings = load_settings()
    notifier = DiscordNotifier(settings.discord_webhook_url)

    if not notifier.enabled:
        print("Set DISCORD_WEBHOOK_URL in .env first.")
        return 1

    notifier.send("Paper Trader test alert — Discord notifications are working.")
    print("Test alert sent. Check your phone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
