from dataclasses import replace

import pandas as pd

from paper_trader.strategy.sma_crossover import Signal, StrategyResult


def refine_with_wisdom(result: StrategyResult, bars: pd.DataFrame) -> StrategyResult:
    """Only act when the signal aligns with simple trend common sense."""
    if result.signal == Signal.BUY:
        close = float(bars["close"].iloc[-1])
        if close <= result.slow_sma:
            return replace(
                result,
                signal=Signal.HOLD,
                reason="BUY crossover but price still below slow average — waiting",
            )
        if result.fast_sma <= result.slow_sma:
            return replace(
                result,
                signal=Signal.HOLD,
                reason="BUY crossover weak — averages not clearly bullish",
            )

    if result.signal == Signal.SELL:
        close = float(bars["close"].iloc[-1])
        if close >= result.slow_sma:
            return replace(
                result,
                signal=Signal.HOLD,
                reason="SELL crossover but price still above slow average — holding",
            )

    return result
