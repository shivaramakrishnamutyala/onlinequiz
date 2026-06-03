import time
import pytest
from unittest.mock import MagicMock, patch, call
from models.quiz               import Quiz
from models.mcq_question       import MCQQuestion
from services.quiz_service     import QuizService
from services.scoring_service  import DetailedScoring
from services.question_timer   import QuestionTimer
from services.quiz_timer       import QuizTimer
from interfaces.timer_interface import TimerInterface

def _make_service(questions, answers, q_limit=20, quiz_limit=60):
    quiz     = Quiz(questions)
    scoring  = DetailedScoring()
    q_timer  = QuestionTimer(limit_seconds=q_limit)
    qz_timer = QuizTimer(limit_seconds=quiz_limit)

    service = QuizService(
        quiz=quiz,
        scoring_strategy=scoring,
        question_timer=q_timer,
        quiz_timer=qz_timer,
    )
    return service, answers

def _run_with_answers(service, answers):
    answer_iter = iter(answers)
    def fake_get_input(self_inner, prompt):
        return next(answer_iter, None)
    with patch(
        "services.quiz_service.TimedInputService.get_input",
        fake_get_input,
    ):
        service.conduct_quiz()

class TestQuizServiceConductQuiz:
    def test_all_correct_score(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q, q, q], ["A", "A", "A"])
        _run_with_answers(service, answers)
        out = capsys.readouterr().out
        assert "Final Score : 30" in out
    def test_all_correct_summary_counts(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q, q], ["A", "A"])
        _run_with_answers(service, answers)
        out = capsys.readouterr().out
        assert "Correct     : 2" in out
        assert "Wrong       : 0" in out
        assert "No answer   : 0" in out

    def test_all_wrong_score(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q, q], ["B", "B"])
        _run_with_answers(service, answers)
        out = capsys.readouterr().out
        assert "Final Score : -10" in out

    def test_all_wrong_summary_counts(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q, q], ["B", "B"])
        _run_with_answers(service, answers)
        out = capsys.readouterr().out
        assert "Wrong       : 2" in out
        assert "Correct     : 0" in out

    def test_all_skipped_score_is_zero(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q, q, q], [None, None, None])
        _run_with_answers(service, answers)
        out = capsys.readouterr().out
        assert "Final Score : 0" in out

    def test_all_skipped_summary_counts(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q, q], [None, None])
        _run_with_answers(service, answers)
        out = capsys.readouterr().out
        assert "No answer   : 2" in out
        assert "Correct     : 0" in out
        assert "Wrong       : 0" in out

    def test_mixed_correct_wrong_skipped_score(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q, q, q], ["A", "B", None])
        _run_with_answers(service, answers)
        out = capsys.readouterr().out
        assert "Final Score : 5" in out

    def test_mixed_summary_counts(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q, q, q], ["A", "B", None])
        _run_with_answers(service, answers)
        out = capsys.readouterr().out
        assert "Correct     : 1" in out
        assert "Wrong       : 1" in out
        assert "No answer   : 1" in out

    def test_output_contains_quiz_started(self, capsys):
        q = MCQQuestion("Q?", ["A"], "A")
        service, answers = _make_service([q], ["A"])
        _run_with_answers(service, answers)
        assert "QUIZ STARTED" in capsys.readouterr().out

    def test_output_contains_quiz_complete(self, capsys):
        q = MCQQuestion("Q?", ["A"], "A")
        service, answers = _make_service([q], ["A"])
        _run_with_answers(service, answers)
        assert "QUIZ COMPLETE" in capsys.readouterr().out

    def test_output_shows_correct_feedback(self, capsys):
        q = MCQQuestion("Q?", ["A"], "A")
        service, answers = _make_service([q], ["A"])
        _run_with_answers(service, answers)
        assert "Correct" in capsys.readouterr().out

    def test_output_shows_wrong_feedback(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q], ["B"])
        _run_with_answers(service, answers)
        assert "Wrong" in capsys.readouterr().out

    def test_output_shows_times_up_feedback(self, capsys):
        q = MCQQuestion("Q?", ["A"], "A")
        service, answers = _make_service([q], [None])
        _run_with_answers(service, answers)
        assert "Time's up" in capsys.readouterr().out

    def test_output_shows_correct_answer_on_wrong(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q], ["B"])
        _run_with_answers(service, answers)
        assert "A" in capsys.readouterr().out   # correct answer revealed

    def test_output_shows_correct_answer_on_skip(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        service, answers = _make_service([q], [None])
        _run_with_answers(service, answers)
        assert "A" in capsys.readouterr().out

    def test_quiz_timer_expiry_ends_quiz_early(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        quiz     = Quiz([q, q, q])
        scoring  = DetailedScoring()
        q_timer  = QuestionTimer(limit_seconds=20)
        qz_timer = QuizTimer(limit_seconds=60)

        service = QuizService(
            quiz=quiz,
            scoring_strategy=scoring,
            question_timer=q_timer,
            quiz_timer=qz_timer,
        )

        mono_values = iter([0, 0, 0, 0, 61, 61])

        def fake_get_input(self_inner, prompt):
            return "A"

        with patch("services.quiz_service.TimedInputService.get_input", fake_get_input):
            with patch("services.quiz_service.time.monotonic", side_effect=mono_values):
                service.conduct_quiz()

        out = capsys.readouterr().out
        assert "Quiz ended early" in out or "time is up" in out.lower()

    def test_remaining_questions_skipped_when_quiz_expires(self, capsys):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        quiz     = Quiz([q, q, q])
        scoring  = DetailedScoring()
        q_timer  = QuestionTimer(limit_seconds=20)
        qz_timer = QuizTimer(limit_seconds=60)

        service = QuizService(
            quiz=quiz,
            scoring_strategy=scoring,
            question_timer=q_timer,
            quiz_timer=qz_timer,
        )

        mono_values = iter([0, 0, 0, 0, 61, 61])

        def fake_get_input(self_inner, prompt):
            return "A"

        with patch("services.quiz_service.TimedInputService.get_input", fake_get_input):
            with patch("services.quiz_service.time.monotonic", side_effect=mono_values):
                service.conduct_quiz()

        out = capsys.readouterr().out
        assert "Final Score : 10" in out

    def test_scoring_strategy_called_with_correct_breakdown(self):
        q = MCQQuestion("Q?", ["A", "B"], "A")
        mock_scoring = MagicMock()
        mock_scoring.calculate_score.return_value = 99

        quiz    = Quiz([q, q, q])
        service = QuizService(
            quiz=quiz,
            scoring_strategy=mock_scoring,
            question_timer=QuestionTimer(20),
            quiz_timer=QuizTimer(60),
        )

        def fake_get_input(self_inner, prompt):
            return "A" 

        with patch("services.quiz_service.TimedInputService.get_input", fake_get_input):
            service.conduct_quiz()

        mock_scoring.calculate_score.assert_called_once_with(
            correct=3, wrong=0, skipped=0
        )

    def test_effective_limit_uses_min_of_question_and_quiz_remaining(self):
        q = MCQQuestion("Q?", ["A"], "A")
        quiz    = Quiz([q])
        service = QuizService(
            quiz=quiz,
            scoring_strategy=DetailedScoring(),
            question_timer=QuestionTimer(limit_seconds=20),
            quiz_timer=QuizTimer(limit_seconds=60),
        )

        captured_timeouts = []

        class CapturingTimedInput:
            def __init__(self_inner, timeout_seconds):
                captured_timeouts.append(timeout_seconds)
                self_inner._timeout = timeout_seconds

            def get_input(self_inner, prompt):
                return "A"
        mono_values = iter([0, 55, 55, 55, 55])

        with patch("services.quiz_service.TimedInputService", CapturingTimedInput):
            with patch("services.quiz_service.time.monotonic", side_effect=mono_values):
                service.conduct_quiz()

        assert captured_timeouts[0] == pytest.approx(5.0)
