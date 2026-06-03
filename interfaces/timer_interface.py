from abc import ABC, abstractmethod
class TimerInterface(ABC):
    @abstractmethod
    def get_limit(self) -> int:
        pass
    @abstractmethod
    def is_expired(self, elapsed: float) -> bool:
        pass
    @abstractmethod
    def remaining(self, elapsed: float) -> float:
        pass
