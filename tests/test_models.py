import pytest
from models.mcq_question       import MCQQuestion
from models.truefalse_question import TrueFalseQuestion
from models.fillblank_question import FillBlankQuestion
from models.question           import Question
from models.quiz               import Quiz

class TestQuestionBase:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            Question("text", "answer")
    def test_stores_question_text_and_correct_answer(self, mcq):
        assert mcq.question_text  == "Which language is used for AI?"
        assert mcq.correct_answer == "Python"

class TestMCQQuestion:
    def test_stores_options(self, mcq):
        assert mcq.options == ["Python", "HTML", "CSS", "SQL"]
    def test_check_answer_correct_exact_case(self, mcq):
        assert mcq.check_answer("Python") is True
    def test_check_answer_correct_lowercase(self, mcq):
        assert mcq.check_answer("python") is True
    def test_check_answer_correct_uppercase(self, mcq):
        assert mcq.check_answer("PYTHON") is True
    def test_check_answer_wrong(self, mcq):
        assert mcq.check_answer("HTML") is False
    def test_check_answer_empty_string(self, mcq):
        assert mcq.check_answer("") is False
    def test_display_prints_question_and_options(self, mcq, capsys):
        mcq.display()
        captured = capsys.readouterr().out
        assert "MCQ Question"                       in captured
        assert "Which language is used for AI?"     in captured
        assert "Python"                             in captured
        assert "HTML"                               in captured
        assert "CSS"                                in captured
        assert "SQL"                                in captured

    def test_display_shows_numbered_options(self, mcq, capsys):
        mcq.display()
        captured = capsys.readouterr().out
        assert "1." in captured
        assert "2." in captured
        assert "3." in captured
        assert "4." in captured

    def test_inherits_from_question(self, mcq):
        assert isinstance(mcq, Question)

class TestTrueFalseQuestion:
    def test_check_answer_correct_lowercase(self, truefalse):
        assert truefalse.check_answer("false") is True
    def test_check_answer_correct_uppercase(self, truefalse):
        assert truefalse.check_answer("FALSE") is True
    def test_check_answer_correct_mixed_case(self, truefalse):
        assert truefalse.check_answer("False") is True
    def test_check_answer_wrong(self, truefalse):
        assert truefalse.check_answer("true") is False
    def test_check_answer_empty_string(self, truefalse):
        assert truefalse.check_answer("") is False
    def test_display_prints_question(self, truefalse, capsys):
        truefalse.display()
        captured = capsys.readouterr().out
        assert "True/False Question"           in captured
        assert "Python is statically typed."   in captured
    def test_inherits_from_question(self, truefalse):
        assert isinstance(truefalse, Question)
    def test_stores_correct_answer(self, truefalse):
        assert truefalse.correct_answer == "false"

class TestFillBlankQuestion:
    def test_check_answer_correct_exact(self, fillblank):
        assert fillblank.check_answer("class") is True
    def test_check_answer_correct_uppercase(self, fillblank):
        assert fillblank.check_answer("CLASS") is True
    def test_check_answer_strips_whitespace(self, fillblank):
        assert fillblank.check_answer("  class  ") is True
    def test_check_answer_strips_and_case_insensitive(self, fillblank):
        assert fillblank.check_answer("  CLASS  ") is True
    def test_check_answer_wrong(self, fillblank):
        assert fillblank.check_answer("def") is False
    def test_check_answer_empty_string(self, fillblank):
        assert fillblank.check_answer("") is False
    def test_display_prints_question(self, fillblank, capsys):
        fillblank.display()
        captured = capsys.readouterr().out
        assert "Fill in the Blank"                  in captured
        assert "___ is used for OOP in Python."     in captured

    def test_inherits_from_question(self, fillblank):
        assert isinstance(fillblank, Question)

class TestQuiz:
    def test_stores_questions(self, sample_quiz, mcq, truefalse, fillblank):
        assert len(sample_quiz.questions) == 3
        assert sample_quiz.questions[0]   is mcq
        assert sample_quiz.questions[1]   is truefalse
        assert sample_quiz.questions[2]   is fillblank
    def test_empty_quiz(self):
        quiz = Quiz([])
        assert quiz.questions == []
    def test_single_question_quiz(self, mcq):
        quiz = Quiz([mcq])
        assert len(quiz.questions) == 1
