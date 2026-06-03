from interfaces.score_strategy import ScoreStrategy
class DetailedScoring(ScoreStrategy):
    CORRECT_MARKS  =  10
    WRONG_MARKS    =  -5
    SKIPPED_MARKS  =   0
    def calculate_score(
        self,
        correct: int,
        wrong: int,
        skipped: int,
    ) -> int:
        return (
            correct  * self.CORRECT_MARKS
            + wrong  * self.WRONG_MARKS
            + skipped * self.SKIPPED_MARKS
        )
