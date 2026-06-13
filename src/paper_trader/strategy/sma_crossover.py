from dataclasses import dataclass
from enum import Enum

import pandas as pd


class Signal(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass(frozen=True)
class StrategyResult:
    signal: Signal
    fast_sma: float
    slow_sma: float
    reason: str


def evaluate_sma_crossover(
    bars: pd.DataFrame,
    fast_period: int = 10,
    slow_period: int = 20,
) -> StrategyResult:
    if len(bars) < slow_period + 2:
        raise ValueError(
            f"Need at least {slow_period + 2} bars, got {len(bars)}"
        )

    closes = bars["close"]
    fast = closes.rolling(fast_period).mean()
    slow = closes.rolling(slow_period).mean()

    prev_fast, prev_slow = fast.iloc[-2], slow.iloc[-2]
    curr_fast, curr_slow = fast.iloc[-1], slow.iloc[-1]

    if pd.isna(prev_fast) or pd.isna(prev_slow) or pd.isna(curr_fast) or pd.isna(curr_slow):
        return StrategyResult(
            signal=Signal.HOLD,
            fast_sma=float(curr_fast) if not pd.isna(curr_fast) else 0.0,
            slow_sma=float(curr_slow) if not pd.isna(curr_slow) else 0.0,
            reason="Not enough data for moving averages",
        )

    crossed_up = prev_fast <= prev_slow and curr_fast > curr_slow
    crossed_down = prev_fast >= prev_slow and curr_fast < curr_slow

    if crossed_up:
        signal = Signal.BUY
        reason = f"SMA{fast_period} crossed above SMA{slow_period}"
    elif crossed_down:
        signal = Signal.SELL
        reason = f"SMA{fast_period} crossed below SMA{slow_period}"
    else:
        signal = Signal.HOLD
        reason = "No crossover"

    return StrategyResult(
        signal=signal,
        fast_sma=float(curr_fast),
        slow_sma=float(curr_slow),
        reason=reason,
    )
