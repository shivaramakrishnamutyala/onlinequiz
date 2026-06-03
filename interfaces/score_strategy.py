from abc import ABC, abstractmethod
class ScoreStrategy(ABC):
    @abstractmethod
    def calculate_score(
        self,
        correct: int,
        wrong: int,
        skipped: int,
    ) -> int:
        pass