import json
from dataclasses import asdict, dataclass
from pathlib import Path

STATE_PATH = Path("state/portfolio.json")


@dataclass
class PortfolioState:
    initial_capital: float
    realized_pnl: float = 0.0
    halted: bool = False

    @classmethod
    def load(cls, initial_capital: float) -> "PortfolioState":
        if not STATE_PATH.exists():
            return cls(initial_capital=initial_capital)

        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return cls(
            initial_capital=float(data.get("initial_capital", initial_capital)),
            realized_pnl=float(data.get("realized_pnl", 0.0)),
            halted=bool(data.get("halted", False)),
        )

    def save(self) -> None:
        STATE_PATH.parent.mkdir(exist_ok=True)
        STATE_PATH.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
