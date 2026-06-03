from models.mcq_question import MCQQuestion
from models.truefalse_question import TrueFalseQuestion
from models.fillblank_question import FillBlankQuestion
from models.quiz import Quiz
from services.scoring_service import DetailedScoring
from services.question_timer import QuestionTimer
from services.quiz_timer import QuizTimer
from services.quiz_service import QuizService

q1 = MCQQuestion(
    "Which language is used for AI?",
    ["Python", "HTML", "CSS", "SQL"],
    "Python"
)
q2 = TrueFalseQuestion(
    "Python is statically typed.",
    "false"
)
q3 = FillBlankQuestion(
    "___ is used for OOP in Python.",
    "class"
)
questions = [q1, q2, q3]

quiz = Quiz(questions)

scoring          = DetailedScoring()
question_timer   = QuestionTimer(limit_seconds=20)   
quiz_timer       = QuizTimer(limit_seconds=60)      

quiz_service = QuizService(
    quiz=quiz,
    scoring_strategy=scoring,
    question_timer=question_timer,
    quiz_timer=quiz_timer,
)

quiz_service.conduct_quiz()
