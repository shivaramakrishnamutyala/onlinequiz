from models.question import Question
class TrueFalseQuestion(Question):
    def check_answer(self, answer):
        return (
            answer.lower()
            ==
            self.correct_answer.lower()
        )
    def display(self):

        print("\nTrue/False Question")
        print(self.question_text)