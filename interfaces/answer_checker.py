from abc import ABC, abstractmethod
class AnswerChecker(ABC):
    @abstractmethod
    def check_answer(self, answer):
        pass