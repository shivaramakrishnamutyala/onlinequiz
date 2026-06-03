from models.question import Question
class FillBlankQuestion(Question):
    def check_answer(self, answer):
        return (
            answer.strip().lower() == self.correct_answer.lower()
        )
    def display(self):
        print("\nFill in the Blank")
        print(self.question_text)