import logging

import requests

logger = logging.getLogger(__name__)


class DiscordNotifier:
    def __init__(self, webhook_url: str | None) -> None:
        self.webhook_url = webhook_url.strip() if webhook_url else None

    @property
    def enabled(self) -> bool:
        return bool(self.webhook_url)

    def send(self, message: str) -> None:
        if not self.enabled:
            return

        try:
            response = requests.post(
                self.webhook_url,
                json={"content": message},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Discord alert failed: %s", exc)
