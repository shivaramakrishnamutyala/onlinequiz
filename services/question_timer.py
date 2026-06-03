from interfaces.timer_interface import TimerInterface
class QuestionTimer(TimerInterface):
    def __init__(self, limit_seconds: int = 20):
        self._limit = limit_seconds
    def get_limit(self) -> int:
        return self._limit
    def is_expired(self, elapsed: float) -> bool:
        return elapsed >= self._limit
    def remaining(self, elapsed: float) -> float:
        return max(0.0, self._limit - elapsed)
