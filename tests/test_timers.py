import pytest
from services.question_timer   import QuestionTimer
from services.quiz_timer       import QuizTimer
from interfaces.timer_interface import TimerInterface

class TestQuestionTimer:
    def test_default_limit_is_20(self):
        timer = QuestionTimer()
        assert timer.get_limit() == 20

    def test_custom_limit(self):
        timer = QuestionTimer(limit_seconds=30)
        assert timer.get_limit() == 30

    def test_implements_timer_interface(self, question_timer):
        assert isinstance(question_timer, TimerInterface)

    def test_get_limit_returns_configured_value(self, question_timer):
        assert question_timer.get_limit() == 20

    def test_not_expired_before_limit(self, question_timer):
        assert question_timer.is_expired(19.9) is False

    def test_expired_exactly_at_limit(self, question_timer):
        assert question_timer.is_expired(20.0) is True

    def test_expired_beyond_limit(self, question_timer):
        assert question_timer.is_expired(25.0) is True

    def test_not_expired_at_zero(self, question_timer):
        assert question_timer.is_expired(0.0) is False

    def test_remaining_before_limit(self, question_timer):
        assert question_timer.remaining(5.0) == pytest.approx(15.0)

    def test_remaining_at_zero_elapsed(self, question_timer):
        assert question_timer.remaining(0.0) == pytest.approx(20.0)

    def test_remaining_exactly_at_limit(self, question_timer):
        assert question_timer.remaining(20.0) == pytest.approx(0.0)

    def test_remaining_never_goes_negative(self, question_timer):
        assert question_timer.remaining(30.0) == pytest.approx(0.0)

    def test_remaining_one_second_left(self, question_timer):
        assert question_timer.remaining(19.0) == pytest.approx(1.0)

class TestQuizTimer:
    def test_default_limit_is_60(self):
        timer = QuizTimer()
        assert timer.get_limit() == 60
    def test_custom_limit(self):
        timer = QuizTimer(limit_seconds=120)
        assert timer.get_limit() == 120
    def test_implements_timer_interface(self, quiz_timer):
        assert isinstance(quiz_timer, TimerInterface)
    def test_get_limit_returns_configured_value(self, quiz_timer):
        assert quiz_timer.get_limit() == 60
    def test_not_expired_before_limit(self, quiz_timer):
        assert quiz_timer.is_expired(59.9) is False

    def test_expired_exactly_at_limit(self, quiz_timer):
        assert quiz_timer.is_expired(60.0) is True

    def test_expired_beyond_limit(self, quiz_timer):
        assert quiz_timer.is_expired(100.0) is True

    def test_not_expired_at_zero(self, quiz_timer):
        assert quiz_timer.is_expired(0.0) is False
    def test_remaining_before_limit(self, quiz_timer):
        assert quiz_timer.remaining(10.0) == pytest.approx(50.0)

    def test_remaining_at_zero_elapsed(self, quiz_timer):
        assert quiz_timer.remaining(0.0) == pytest.approx(60.0)

    def test_remaining_exactly_at_limit(self, quiz_timer):
        assert quiz_timer.remaining(60.0) == pytest.approx(0.0)

    def test_remaining_never_goes_negative(self, quiz_timer):
        assert quiz_timer.remaining(999.0) == pytest.approx(0.0)

    def test_remaining_half_elapsed(self, quiz_timer):
        assert quiz_timer.remaining(30.0) == pytest.approx(30.0)
