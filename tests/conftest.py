import pytest
from models.mcq_question      import MCQQuestion
from models.truefalse_question import TrueFalseQuestion
from models.fillblank_question import FillBlankQuestion
from models.quiz               import Quiz
from services.scoring_service  import DetailedScoring
from services.question_timer   import QuestionTimer
from services.quiz_timer       import QuizTimer

@pytest.fixture
def mcq():
    return MCQQuestion(
        "Which language is used for AI?",
        ["Python", "HTML", "CSS", "SQL"],
        "Python",
    )

@pytest.fixture
def truefalse():
    return TrueFalseQuestion(
        "Python is statically typed.",
        "false",
    )

@pytest.fixture
def fillblank():
    return FillBlankQuestion(
        "___ is used for OOP in Python.",
        "class",
    )

@pytest.fixture
def sample_quiz(mcq, truefalse, fillblank):
    return Quiz([mcq, truefalse, fillblank])

@pytest.fixture
def scoring():
    return DetailedScoring()
@pytest.fixture
def question_timer():
    return QuestionTimer(limit_seconds=20)

@pytest.fixture
def quiz_timer():
    return QuizTimer(limit_seconds=60)
