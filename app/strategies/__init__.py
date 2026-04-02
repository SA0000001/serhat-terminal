from app.strategies.registry import StrategyRegistry
from app.strategies.sma_cross import SmaCrossStrategy
from app.strategies.breakout import BreakoutStrategy
from app.strategies.mean_reversion import MeanReversionStrategy

registry = StrategyRegistry()
registry.register(SmaCrossStrategy())
registry.register(BreakoutStrategy())
registry.register(MeanReversionStrategy())
