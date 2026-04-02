from app.strategies.base import StrategyBase


class StrategyRegistry:
    def __init__(self) -> None:
        self._items: dict[str, StrategyBase] = {}

    def register(self, strategy: StrategyBase) -> None:
        self._items[strategy.name] = strategy

    def get(self, name: str) -> StrategyBase:
        return self._items[name]

    def all(self) -> list[StrategyBase]:
        return list(self._items.values())
