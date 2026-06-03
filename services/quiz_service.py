import time
from interfaces.timer_interface import TimerInterface
from services.timed_input_service import TimedInputService
class QuizService:
    def __init__(
        self,
        quiz,
        scoring_strategy,
        question_timer: TimerInterface,
        quiz_timer: TimerInterface,
    ):
        self._quiz             = quiz
        self._scoring_strategy = scoring_strategy
        self._question_timer   = question_timer
        self._quiz_timer       = quiz_timer

    def conduct_quiz(self) -> None:
        print("\n" + "=" * 50)
        print("  QUIZ STARTED")
        print(f"  Total time  : {self._quiz_timer.get_limit()} seconds")
        print(f"  Per question: {self._question_timer.get_limit()} seconds")
        print("  Marking     : Correct +10 | Wrong -5 | No answer 0")
        print("=" * 50)

        correct = 0
        wrong   = 0
        skipped = 0

        quiz_start = time.monotonic()

        for index, question in enumerate(self._quiz.questions, start=1):
            quiz_elapsed = time.monotonic() - quiz_start
            if self._quiz_timer.is_expired(quiz_elapsed):
                print("\nOverall quiz time is up! Quiz ended early.")
                skipped += len(self._quiz.questions) - (index - 1)
                break

            quiz_remaining  = self._quiz_timer.remaining(quiz_elapsed)
            effective_limit = min(
                self._question_timer.get_limit(),
                quiz_remaining,
            )

            print(f"\n[Question {index}/{len(self._quiz.questions)}]", end="  ")
            print(
                f" Quiz time left: {quiz_remaining:.0f}s  |  "
                f"This question: {effective_limit:.0f}s"
            )

            question.display()
            timed_input = TimedInputService(timeout_seconds=effective_limit)
            q_start     = time.monotonic()
            answer      = timed_input.get_input("Your Answer: ")
            q_elapsed   = time.monotonic() - q_start
            if answer is None or self._question_timer.is_expired(q_elapsed):
                skipped += 1
                print(
                    f"Time's up!  "
                    f"Correct answer was: {question.correct_answer}  "
                    f"[+0 marks]"
                )

            elif question.check_answer(answer):
                correct += 1
                print("Correct!  [+10 marks]")

            else:
                # Wrong answer → -5 marks
                wrong += 1
                print(
                    f"Wrong!  "
                    f"Correct answer was: {question.correct_answer}  "
                    f"[-5 marks]"
                )
        total_elapsed = time.monotonic() - quiz_start
        score = self._scoring_strategy.calculate_score(
            correct=correct,
            wrong=wrong,
            skipped=skipped,
        )
        print("\n" + "=" * 50)
        print("  QUIZ COMPLETE")
        print(f"  Time taken  : {total_elapsed:.1f}s")
        print(f"  Correct     : {correct}  (+{correct * 10} marks)")
        print(f"  Wrong       : {wrong}  ({wrong * -5} marks)")
        print(f"  No answer   : {skipped}  (0 marks)")
        print(f"  Final Score : {score}")
        print("=" * 50 + "\n")
