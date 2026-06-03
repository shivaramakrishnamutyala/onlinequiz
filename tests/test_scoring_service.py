import pytest
from services.scoring_service import DetailedScoring

class TestDetailedScoring:
    def test_correct_marks_constant(self):
        assert DetailedScoring.CORRECT_MARKS == 10
    def test_wrong_marks_constant(self):
        assert DetailedScoring.WRONG_MARKS == -5
    def test_skipped_marks_constant(self):
        assert DetailedScoring.SKIPPED_MARKS == 0

    def test_all_correct(self, scoring):
        assert scoring.calculate_score(correct=3, wrong=0, skipped=0) == 30

    def test_one_correct(self, scoring):
        assert scoring.calculate_score(correct=1, wrong=0, skipped=0) == 10

    def test_all_wrong(self, scoring):
        assert scoring.calculate_score(correct=0, wrong=3, skipped=0) == -15

    def test_one_wrong(self, scoring):
        assert scoring.calculate_score(correct=0, wrong=1, skipped=0) == -5

    def test_all_skipped(self, scoring):
        assert scoring.calculate_score(correct=0, wrong=0, skipped=3) == 0

    def test_one_skipped(self, scoring):
        assert scoring.calculate_score(correct=0, wrong=0, skipped=1) == 0

    def test_correct_and_wrong(self, scoring):
        assert scoring.calculate_score(correct=2, wrong=1, skipped=0) == 15

    def test_correct_and_skipped(self, scoring):
        assert scoring.calculate_score(correct=1, wrong=0, skipped=2) == 10

    def test_wrong_and_skipped(self, scoring):
        assert scoring.calculate_score(correct=0, wrong=2, skipped=1) == -10

    def test_all_three_mixed(self, scoring):
        assert scoring.calculate_score(correct=2, wrong=1, skipped=1) == 15

    def test_all_zeros(self, scoring):
        assert scoring.calculate_score(correct=0, wrong=0, skipped=0) == 0

    def test_score_can_be_negative(self, scoring):
        assert scoring.calculate_score(correct=0, wrong=4, skipped=0) == -20

    def test_score_exact_zero_balance(self, scoring):
        assert scoring.calculate_score(correct=1, wrong=2, skipped=0) == 0

    def test_large_numbers(self, scoring):
        assert scoring.calculate_score(correct=100, wrong=50, skipped=20) == 750
