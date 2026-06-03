from abc import ABC
from interfaces.answer_checker import AnswerChecker
class Question(AnswerChecker, ABC):

    def __init__(self, question_text, correct_answer):
        self.question_text = question_text
        self.correct_answer = correct_answer