import json
from dataclasses import asdict, dataclass
from pathlib import Path

from paper_trader.paths import CRYPTO_STATE_PATH, STOCK_STATE_PATH


@dataclass
class PortfolioState:
    initial_capital: float
    realized_pnl: float = 0.0
    halted: bool = False
    state_path: Path = STOCK_STATE_PATH

    @classmethod
    def load(
        cls,
        initial_capital: float,
        state_path: Path = STOCK_STATE_PATH,
    ) -> "PortfolioState":
        if not state_path.exists():
            return cls(initial_capital=initial_capital, state_path=state_path)

        data = json.loads(state_path.read_text(encoding="utf-8"))
        return cls(
            initial_capital=float(data.get("initial_capital", initial_capital)),
            realized_pnl=float(data.get("realized_pnl", 0.0)),
            halted=bool(data.get("halted", False)),
            state_path=state_path,
        )

    def save(self) -> None:
        self.state_path.parent.mkdir(exist_ok=True)
        payload = {
            "initial_capital": self.initial_capital,
            "realized_pnl": self.realized_pnl,
            "halted": self.halted,
        }
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
