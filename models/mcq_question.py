from models.question import Question
class MCQQuestion(Question):
    def __init__(
        self,
        question_text,
        options,
        correct_answer
    ):

        super().__init__(
            question_text,
            correct_answer
        )

        self.options = options

    def check_answer(self, answer):

        return (
            answer.lower()
            ==
            self.correct_answer.lower()
        )

    def display(self):

        print("\nMCQ Question")
        print(self.question_text)

        for index, option in enumerate(self.options, start=1):
            print(f"{index}. {option}")