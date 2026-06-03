import pytest
from interfaces.answer_checker  import AnswerChecker
from interfaces.score_strategy  import ScoreStrategy
from interfaces.timer_interface import TimerInterface

class TestAnswerCheckerInterface:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            AnswerChecker()
    def test_concrete_subclass_without_check_answer_raises(self):
        class Incomplete(AnswerChecker):
            pass
        with pytest.raises(TypeError):
            Incomplete()

    def test_concrete_subclass_with_check_answer_works(self):
        class Concrete(AnswerChecker):
            def check_answer(self, answer):
                return answer == "yes"
        obj = Concrete()
        assert obj.check_answer("yes")  is True
        assert obj.check_answer("no")   is False

class TestScoreStrategyInterface:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            ScoreStrategy()
    def test_concrete_subclass_without_calculate_score_raises(self):
        class Incomplete(ScoreStrategy):
            pass
        with pytest.raises(TypeError):
            Incomplete()
    def test_concrete_subclass_with_calculate_score_works(self):
        class Concrete(ScoreStrategy):
            def calculate_score(self, correct, wrong, skipped):
                return correct - wrong

        obj = Concrete()
        assert obj.calculate_score(3, 1, 0) == 2

class TestTimerInterface:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            TimerInterface()
    def test_concrete_subclass_missing_methods_raises(self):
        class Incomplete(TimerInterface):
            pass
        with pytest.raises(TypeError):
            Incomplete()
    def test_concrete_subclass_fully_implemented_works(self):
        class Concrete(TimerInterface):
            def get_limit(self):   return 10
            def is_expired(self, e): return e >= 10
            def remaining(self, e):  return max(0.0, 10 - e)
        obj = Concrete()
        assert obj.get_limit()       == 10
        assert obj.is_expired(10)    is True
        assert obj.is_expired(9.9)   is False
        assert obj.remaining(4)      == 6.0
        assert obj.remaining(15)     == 0.0
