# Online Quiz Application

A fully object-oriented, console-based quiz application built in Python.  
It supports multiple question types, per-question time limits, an overall quiz timer, a detailed marking scheme, and a complete unit test suite with 97% code coverage.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [How the Project Was Built — Step by Step](#3-how-the-project-was-built--step-by-step)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Every File Explained](#5-every-file-explained)
6. [SOLID Principles — Detailed Explanation](#6-solid-principles--detailed-explanation)
7. [Marking Scheme](#7-marking-scheme)
8. [Timer System](#8-timer-system)
9. [Running the Quiz](#9-running-the-quiz)
10. [Running the Tests](#10-running-the-tests)
11. [Test Coverage Report](#11-test-coverage-report)
12. [Sample Output](#12-sample-output)

---

## 1. Project Overview

This project is a timed online quiz that runs in the terminal.  
A user is asked a series of questions one by one. Each question has a **20-second** individual time limit and the entire quiz has a **60-second** overall time limit.

| Feature | Detail |
|---|---|
| Question types | MCQ, True/False, Fill-in-the-Blank |
| Per-question time | 20 seconds |
| Overall quiz time | 60 seconds |
| Correct answer | +10 marks |
| Wrong answer | −5 marks |
| No answer (timed out) | 0 marks |
| Test coverage | 97% (109 tests, all passing) |

---

## 2. Project Structure

```
onlinequiz/
│
├── main.py                         ← Entry point. Wires everything together.
│
├── interfaces/                     ← Abstract contracts (pure Python ABCs)
│   ├── answer_checker.py           ← Interface: check_answer()
│   ├── score_strategy.py           ← Interface: calculate_score()
│   └── timer_interface.py          ← Interface: get_limit(), is_expired(), remaining()
│
├── models/                         ← Data / domain objects
│   ├── question.py                 ← Abstract base: stores text + correct answer
│   ├── mcq_question.py             ← Multiple-choice question
│   ├── truefalse_question.py       ← True / False question
│   ├── fillblank_question.py       ← Fill-in-the-blank question
│   └── quiz.py                     ← Container: holds a list of questions
│
├── services/                       ← Business logic
│   ├── scoring_service.py          ← DetailedScoring: +10 / -5 / 0
│   ├── question_timer.py           ← Timer for one question (default 20s)
│   ├── quiz_timer.py               ← Timer for the whole quiz (default 60s)
│   ├── timed_input_service.py      ← Reads user input with a hard timeout
│   └── quiz_service.py             ← Orchestrates the full quiz flow
│
└── tests/                          ← Unit tests
    ├── conftest.py                 ← Shared pytest fixtures
    ├── test_interfaces.py          ← Tests for all 3 abstract interfaces
    ├── test_models.py              ← Tests for all question types + Quiz
    ├── test_scoring_service.py     ← Tests for DetailedScoring
    ├── test_timers.py              ← Tests for QuestionTimer + QuizTimer
    ├── test_timed_input_service.py ← Tests for TimedInputService
    └── test_quiz_service.py        ← Tests for QuizService.conduct_quiz()
```

---

## 3. How the Project Was Built — Step by Step

The project was designed and built in four distinct phases.  
Each phase added a new layer without breaking anything from the previous phase.

---

### Phase 1 — Core Domain (Models + Basic Quiz Flow)

**Goal:** Get a working quiz with questions and a simple scoring system.

The first decision was to define what a "question" is. All question types share two things: they store some text, and they can check an answer. So an **abstract base class** `Question` was created to hold those shared attributes.

```python
# models/question.py
class Question(AnswerChecker, ABC):
    def __init__(self, question_text, correct_answer):
        self.question_text = question_text
        self.correct_answer = correct_answer
```

`AnswerChecker` is an interface (abstract class) that forces every subclass to implement `check_answer()`:

```python
# interfaces/answer_checker.py
class AnswerChecker(ABC):
    @abstractmethod
    def check_answer(self, answer):
        pass
```

Three concrete question types were then created by inheriting from `Question`:

**MCQQuestion** — stores a list of options and checks answers case-insensitively:
```python
class MCQQuestion(Question):
    def __init__(self, question_text, options, correct_answer):
        super().__init__(question_text, correct_answer)
        self.options = options

    def check_answer(self, answer):
        return answer.lower() == self.correct_answer.lower()

    def display(self):
        print("\nMCQ Question")
        print(self.question_text)
        for index, option in enumerate(self.options, start=1):
            print(f"{index}. {option}")
```

**TrueFalseQuestion** — same check logic, simpler display:
```python
class TrueFalseQuestion(Question):
    def check_answer(self, answer):
        return answer.lower() == self.correct_answer.lower()

    def display(self):
        print("\nTrue/False Question")
        print(self.question_text)
```

**FillBlankQuestion** — strips whitespace before comparing:
```python
class FillBlankQuestion(Question):
    def check_answer(self, answer):
        return answer.strip().lower() == self.correct_answer.lower()

    def display(self):
        print("\nFill in the Blank")
        print(self.question_text)
```

A `Quiz` class was created simply as a container to hold the list of questions:

```python
# models/quiz.py
class Quiz:
    def __init__(self, questions):
        self.questions = questions
```

A `ScoreStrategy` interface was defined so that scoring could be swapped out later:

```python
# interfaces/score_strategy.py
class ScoreStrategy(ABC):
    @abstractmethod
    def calculate_score(self, correct: int, wrong: int, skipped: int) -> int:
        pass
```

A basic `QuizService` was written to loop through the questions, collect answers, and print a final score.

At the end of Phase 1, the quiz ran and worked — no timing, basic scoring.

---

### Phase 2 — Detailed Scoring (+10 / −5 / 0)

**Goal:** Replace the flat `correct × 10` formula with a proper marking scheme.

The `ScoreStrategy` interface was updated to accept three separate counts — correct, wrong, and skipped — so that any scoring class could use all three values:

```python
class ScoreStrategy(ABC):
    @abstractmethod
    def calculate_score(self, correct: int, wrong: int, skipped: int) -> int:
        pass
```

`DetailedScoring` was created implementing this interface:

```python
# services/scoring_service.py
class DetailedScoring(ScoreStrategy):
    CORRECT_MARKS  =  10
    WRONG_MARKS    =  -5
    SKIPPED_MARKS  =   0

    def calculate_score(self, correct, wrong, skipped) -> int:
        return (
            correct  * self.CORRECT_MARKS
            + wrong  * self.WRONG_MARKS
            + skipped * self.SKIPPED_MARKS
        )
```

`QuizService` was updated to track three separate counters (`correct`, `wrong`, `skipped`) instead of one, and pass all three to the scoring strategy at the end.

---

### Phase 3 — Timer System (20s per question, 60s overall)

**Goal:** Cut users off after 20 seconds per question and after 60 seconds total.

First, a `TimerInterface` abstract class was created to define what any timer must do:

```python
# interfaces/timer_interface.py
class TimerInterface(ABC):
    @abstractmethod
    def get_limit(self) -> int: pass

    @abstractmethod
    def is_expired(self, elapsed: float) -> bool: pass

    @abstractmethod
    def remaining(self, elapsed: float) -> float: pass
```

Two concrete timer classes were created from it:

```python
# services/question_timer.py
class QuestionTimer(TimerInterface):
    def __init__(self, limit_seconds: int = 20):
        self._limit = limit_seconds

    def get_limit(self) -> int:
        return self._limit

    def is_expired(self, elapsed: float) -> bool:
        return elapsed >= self._limit

    def remaining(self, elapsed: float) -> float:
        return max(0.0, self._limit - elapsed)
```

```python
# services/quiz_timer.py
class QuizTimer(TimerInterface):
    def __init__(self, limit_seconds: int = 60):
        self._limit = limit_seconds
    # ... same three methods, different default
```

A `TimedInputService` was built to handle the trickiest part — cutting off user input mid-type when time runs out. It uses Python's `threading` module: a background daemon thread reads from the terminal while the main thread waits for at most `timeout_seconds`. If the event is not set in time, `None` is returned.

```python
# services/timed_input_service.py
class TimedInputService:
    def __init__(self, timeout_seconds: float):
        self._timeout = timeout_seconds

    def get_input(self, prompt: str) -> str | None:
        answer_container = [None]
        input_received = threading.Event()

        def _read():
            try:
                answer_container[0] = input(prompt)
            except EOFError:
                answer_container[0] = None
            finally:
                input_received.set()

        thread = threading.Thread(target=_read, daemon=True)
        thread.start()

        timed_out = not input_received.wait(timeout=self._timeout)

        if timed_out:
            print()
            return None

        return answer_container[0]
```

`QuizService` was updated to accept both timers via constructor injection, and to calculate an `effective_limit` per question as the minimum of the question timer and whatever quiz time remains:

```python
effective_limit = min(
    self._question_timer.get_limit(),
    quiz_remaining,
)
```

This guarantees that if only 5 seconds of quiz time remain, the question limit is also capped at 5 — so the two timers always stay in sync.

---

### Phase 4 — Unit Tests + Coverage

**Goal:** Test every function, every branch, every edge case. Achieve near-100% coverage.

`pytest` and `pytest-cov` were used. A `tests/` folder was created with one test file per module. A shared `conftest.py` provides reusable fixtures (question objects, timers, scoring instance) across all test files. Mocking with `unittest.mock.patch` was used to:
- Control what `input()` returns without waiting for real keyboard input
- Freeze `time.monotonic()` to simulate timer expiry deterministically
- Replace `TimedInputService` with a capturing stub to verify timeout values

---

## 4. Architecture Diagram

```
main.py
  │
  ├── Quiz ──────────────────── [MCQQuestion, TrueFalseQuestion, FillBlankQuestion]
  │                                       │
  │                               Question (abstract)
  │                                       │
  │                               AnswerChecker (interface)
  │
  ├── DetailedScoring ─────────── ScoreStrategy (interface)
  │
  ├── QuestionTimer ─────────────┐
  │                              ├── TimerInterface (interface)
  ├── QuizTimer ─────────────────┘
  │
  └── QuizService
          │
          ├── uses Quiz
          ├── uses ScoreStrategy  (injected)
          ├── uses TimerInterface (injected × 2)
          └── uses TimedInputService (created per question)
```

---

## 5. Every File Explained

### `interfaces/answer_checker.py`
Defines the contract that any question must follow. Forces the implementor to write `check_answer(answer)`. Without this, nothing prevents a developer from creating a question class with a typo like `checkAnswer()` and getting silent bugs.

### `interfaces/score_strategy.py`
Defines the contract for any scoring system. Accepts `correct`, `wrong`, and `skipped` so that any scoring formula — simple, penalised, weighted — can be implemented by just making a new class.

### `interfaces/timer_interface.py`
Defines what every timer must provide: its limit, whether it has expired, and how many seconds remain. `QuizService` only ever talks to this interface — it does not care whether it's a question timer or a quiz timer.

### `models/question.py`
Abstract base for all question types. Stores `question_text` and `correct_answer`. Cannot be instantiated directly. Inherits from `AnswerChecker`, so all subclasses are forced to implement `check_answer`.

### `models/mcq_question.py`
Multiple choice. Stores `options` (a list). `display()` prints each option numbered. `check_answer()` is case-insensitive.

### `models/truefalse_question.py`
True / False question. No options list. `check_answer()` is case-insensitive — so `"True"`, `"TRUE"`, `"true"` all match.

### `models/fillblank_question.py`
Fill-in-the-blank. `check_answer()` strips leading/trailing whitespace before comparing, so `"  class  "` matches `"class"`.

### `models/quiz.py`
A plain container. Holds a list of question objects. `QuizService` reads `quiz.questions` to iterate through them.

### `services/scoring_service.py`
Implements `ScoreStrategy`. Marking constants are defined as class-level attributes so they are easy to find and change in one place. Formula: `correct × 10 + wrong × (−5) + skipped × 0`.

### `services/question_timer.py`
Implements `TimerInterface` for a single question. Default limit: 20 seconds. `remaining()` uses `max(0.0, ...)` to guarantee the result never goes negative.

### `services/quiz_timer.py`
Same structure as `QuestionTimer` but default limit is 60 seconds.

### `services/timed_input_service.py`
The most technically complex class. Solves the problem that Python's built-in `input()` blocks forever. A background daemon thread calls `input()`, a `threading.Event` signals when it finishes. The main thread waits up to `timeout_seconds`. If the event fires in time, the answer is returned. If not, `None` is returned and the quiz moves on.

### `services/quiz_service.py`
The orchestrator. Receives all dependencies through its constructor. Runs the quiz loop — checking both timers before every question, collecting timed input, categorising each answer as correct / wrong / skipped, and printing a full summary at the end.

### `main.py`
The entry point. Creates all objects and wires them together. This is the only place where concrete classes are named directly. Everything else in the system talks through interfaces.

---

## 6. SOLID Principles — Detailed Explanation

SOLID is a set of five design principles that make software easier to maintain, extend, and test. Every letter stands for one principle. This project applies all five deliberately and consistently.

---

### S — Single Responsibility Principle

> **A class should have only one reason to change.**

Every class in this project has exactly one job. If requirements change, only the class responsible for that area needs to be modified.

| Class | Its single responsibility |
|---|---|
| `Question` | Store question text and the correct answer |
| `MCQQuestion` | Display MCQ format and check MCQ answers |
| `Quiz` | Hold a collection of questions |
| `QuestionTimer` | Track the time limit for one question |
| `QuizTimer` | Track the time limit for the whole quiz |
| `TimedInputService` | Read user input with a hard timeout |
| `DetailedScoring` | Calculate score using +10 / −5 / 0 rules |
| `QuizService` | Orchestrate the quiz flow from start to finish |

**Example — why this matters:**

If you want to change the display format of a True/False question, you only touch `TrueFalseQuestion.display()`. You do not need to open `QuizService`, `Quiz`, or any other file.

If you want to change the marking scheme from +10/−5 to +5/−2, you only touch `DetailedScoring`. You do not need to open `QuizService` or any question class.

**What it looked like before SRP was applied:**

Imagine if `QuizService` also contained the scoring formula directly:

```python
# BAD — QuizService doing scoring's job
score = correct * 10 + wrong * (-5)
```

Now QuizService has two reasons to change: if the quiz flow changes AND if the marking scheme changes. SRP says these must be separated.

---

### O — Open/Closed Principle

> **A class should be open for extension, but closed for modification.**
>
> This means you can add new behaviour by writing a new class, without editing the existing classes that already work.

**Example 1 — Adding a new question type:**

Right now the project has `MCQQuestion`, `TrueFalseQuestion`, and `FillBlankQuestion`. To add a `MatchingQuestion` or `OrderingQuestion`, you simply write a new class that extends `Question`:

```python
class MatchingQuestion(Question):
    def check_answer(self, answer):
        # new logic here
        ...
    def display(self):
        # new display here
        ...
```

You do **not** touch `Quiz`, `QuizService`, or any existing question class. They are **closed** for modification. Your new class **extends** the system.

**Example 2 — Adding a new scoring strategy:**

Today the project uses `DetailedScoring`. Tomorrow, you might want a `BonusScoring` that gives 20 marks for the first correct answer:

```python
class BonusScoring(ScoreStrategy):
    def calculate_score(self, correct, wrong, skipped):
        if correct > 0:
            return 20 + (correct - 1) * 10 + wrong * (-5)
        return wrong * (-5)
```

Again, you do **not** touch `QuizService`. You simply pass `BonusScoring()` instead of `DetailedScoring()` in `main.py`. `QuizService` is closed for modification.

**Example 3 — Adding a new timer type:**

You could create a `StrictTimer` that uses milliseconds, or a `RelaxedTimer` with no expiry at all:

```python
class NoLimitTimer(TimerInterface):
    def get_limit(self):   return 999999
    def is_expired(self, elapsed): return False
    def remaining(self, elapsed):  return 999999.0
```

Pass it into `QuizService` and the quiz runs without any time limit — without changing a single line of `QuizService`.

---

### L — Liskov Substitution Principle

> **Objects of a subclass should be usable anywhere the parent class is expected, without breaking the program.**

In other words: if `QuizService` expects a `TimerInterface`, then passing either a `QuestionTimer` or a `QuizTimer` must work correctly — not just technically compile, but behave correctly.

**Example 1 — Timers are substitutable:**

`QuizService.__init__` takes two `TimerInterface` parameters:

```python
def __init__(
    self,
    quiz,
    scoring_strategy,
    question_timer: TimerInterface,   # ← could be ANY TimerInterface
    quiz_timer:     TimerInterface,   # ← could be ANY TimerInterface
):
```

`QuestionTimer` and `QuizTimer` both implement the full contract of `TimerInterface` correctly:
- `get_limit()` always returns an integer
- `is_expired(elapsed)` returns `True` when `elapsed >= limit`, `False` otherwise
- `remaining(elapsed)` always returns a non-negative float

Because both classes honour the contract fully, they are perfectly interchangeable. You could even pass a `QuizTimer` as the `question_timer` argument and the program would still run without errors.

**Example 2 — Questions are substitutable:**

`QuizService` iterates through `quiz.questions` and calls two methods on each:

```python
question.display()
question.check_answer(answer)
```

It does not know or care whether the current question is an `MCQQuestion`, `TrueFalseQuestion`, or `FillBlankQuestion`. All three implement both methods correctly. Substituting one for another does not break the loop.

**What would violate LSP:**

```python
class BrokenTimer(TimerInterface):
    def get_limit(self):       return "twenty"  # returns a string, not int!
    def is_expired(self, e):   return None       # returns None, not bool!
    def remaining(self, e):    return -5.0       # returns negative!
```

This class technically extends `TimerInterface` but violates the expected behaviour. Passing it into `QuizService` would cause crashes or wrong results. LSP says your subclasses must honour the full contract, not just the method signatures.

---

### I — Interface Segregation Principle

> **A class should not be forced to implement methods it does not need.**
> **Keep interfaces small and focused.**

This project has three separate, focused interfaces rather than one large catch-all:

**`AnswerChecker`** — only one method:
```python
class AnswerChecker(ABC):
    @abstractmethod
    def check_answer(self, answer): pass
```

**`ScoreStrategy`** — only one method:
```python
class ScoreStrategy(ABC):
    @abstractmethod
    def calculate_score(self, correct, wrong, skipped) -> int: pass
```

**`TimerInterface`** — three closely related methods (all about time):
```python
class TimerInterface(ABC):
    @abstractmethod
    def get_limit(self) -> int: pass

    @abstractmethod
    def is_expired(self, elapsed: float) -> bool: pass

    @abstractmethod
    def remaining(self, elapsed: float) -> float: pass
```

**What would violate ISP:**

Imagine combining everything into one interface:

```python
# BAD — one bloated interface
class QuizComponent(ABC):
    @abstractmethod
    def check_answer(self, answer): pass

    @abstractmethod
    def calculate_score(self, correct, wrong, skipped): pass

    @abstractmethod
    def get_limit(self) -> int: pass

    @abstractmethod
    def is_expired(self, elapsed): pass

    @abstractmethod
    def remaining(self, elapsed): pass
```

Now `MCQQuestion` is forced to implement `calculate_score`, `get_limit`, `is_expired`, and `remaining` — methods that have absolutely nothing to do with a question. And `QuestionTimer` is forced to implement `check_answer` and `calculate_score` — things a timer should never know about.

ISP says: split them. Questions only implement `AnswerChecker`. Timers only implement `TimerInterface`. Scoring only implements `ScoreStrategy`.

---

### D — Dependency Inversion Principle

> **High-level modules should not depend on low-level modules. Both should depend on abstractions.**
>
> In practice: inject dependencies through the constructor, and type-hint them as the abstract interface, not the concrete class.

`QuizService` is the clearest example in this project. It is the highest-level class — it orchestrates the entire quiz. Here is its constructor:

```python
# services/quiz_service.py
class QuizService:
    def __init__(
        self,
        quiz,
        scoring_strategy,             # ← ScoreStrategy (abstract)
        question_timer: TimerInterface,  # ← TimerInterface (abstract)
        quiz_timer:     TimerInterface,  # ← TimerInterface (abstract)
    ):
        self._quiz             = quiz
        self._scoring_strategy = scoring_strategy
        self._question_timer   = question_timer
        self._quiz_timer       = quiz_timer
```

Notice what is **not** there:
- No `from services.scoring_service import DetailedScoring` inside `QuizService`
- No `from services.question_timer import QuestionTimer` inside `QuizService`
- No `DetailedScoring()` being constructed inside `QuizService`

`QuizService` never creates its own dependencies. It receives them from outside. This is called **Dependency Injection**.

The only place where concrete classes are wired together is `main.py`:

```python
# main.py — the composition root
scoring        = DetailedScoring()
question_timer = QuestionTimer(limit_seconds=20)
quiz_timer     = QuizTimer(limit_seconds=60)

quiz_service = QuizService(
    quiz=quiz,
    scoring_strategy=scoring,
    question_timer=question_timer,
    quiz_timer=quiz_timer,
)
```

**Why this matters — testability:**

In the unit tests, `QuizService` is tested with a `MagicMock` scoring strategy:

```python
mock_scoring = MagicMock()
mock_scoring.calculate_score.return_value = 99

service = QuizService(
    quiz=quiz,
    scoring_strategy=mock_scoring,   # ← fake injected in place of real one
    question_timer=QuestionTimer(20),
    quiz_timer=QuizTimer(60),
)
```

This is only possible because `QuizService` depends on the abstraction, not the concrete `DetailedScoring` class. If `QuizService` had created `DetailedScoring()` internally, there would be no way to replace it with a mock.

**The flow of dependencies:**

```
main.py (composition root)
    │
    │  creates concretes and injects them
    ▼
QuizService  ──depends on──▶  TimerInterface  ◀──implements──  QuestionTimer
             ──depends on──▶  TimerInterface  ◀──implements──  QuizTimer
             ──depends on──▶  ScoreStrategy   ◀──implements──  DetailedScoring
```

The arrows from `QuizService` point at the **interfaces**, not the concrete classes. The concrete classes (bottom row) depend on the interfaces too, by implementing them. Both sides depend on the abstraction in the middle.

---

## 7. Marking Scheme

| Outcome | Marks |
|---|---|
| Correct answer | +10 |
| Wrong answer | −5 |
| No answer (timeout) | 0 |

**Examples:**

| Correct | Wrong | Skipped | Score |
|---|---|---|---|
| 3 | 0 | 0 | 30 |
| 2 | 1 | 0 | 15 |
| 1 | 0 | 2 | 10 |
| 0 | 3 | 0 | −15 |
| 1 | 2 | 0 | 0 |

Skipped questions never add or deduct marks. This is by design: if a user runs out of time, they are not penalised — they simply did not answer.

---

## 8. Timer System

Two independent timers run simultaneously during the quiz.

### Per-question timer (QuestionTimer — 20 seconds)

Starts when a question is displayed. If the user does not type an answer and press Enter within 20 seconds, `TimedInputService` returns `None` and the question is marked as skipped.

### Overall quiz timer (QuizTimer — 60 seconds)

Starts when the quiz begins. Before every question, the elapsed time is checked. If 60 seconds have passed, the quiz ends immediately and all remaining questions are counted as skipped.

### Effective limit

Before each question, the effective time limit given to `TimedInputService` is the **minimum** of the question timer and the quiz time remaining:

```python
effective_limit = min(
    self._question_timer.get_limit(),  # 20s
    quiz_remaining,                    # e.g. 5s if near the end
)
```

This means: if only 5 seconds of quiz time remain, the user gets 5 seconds for that question — not 20. The timers stay in sync.

---

## 9. Running the Quiz

```cmd
cd C:\Users\ADMIN\Desktop\onlinequiz
python main.py
```

---

## 10. Running the Tests

Navigate to the project root first:

```cmd
cd C:\Users\ADMIN\Desktop\onlinequiz
```

| Command | What it does |
|---|---|
| `python -m pytest` | Run all 109 tests |
| `python -m pytest -v` | Run all tests with each test name printed |
| `python -m pytest -v --cov=. --cov-report=term-missing` | Run all tests + full coverage report |
| `python -m pytest tests/test_scoring_service.py -v` | Run only scoring tests |
| `python -m pytest tests/test_timers.py -v` | Run only timer tests |
| `python -m pytest tests/test_quiz_service.py -v` | Run only quiz service tests |

> **Note:** Always use `python -m pytest` on Windows if the `pytest` command is not on your PATH.

---

## 11. Test Coverage Report

```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
interfaces\answer_checker.py            5      1    80%
interfaces\score_strategy.py            5      1    80%
interfaces\timer_interface.py          11      3    73%
main.py                                18     18     0%
models\fillblank_question.py            7      0   100%
models\mcq_question.py                 12      0   100%
models\question.py                      6      0   100%
models\quiz.py                          3      0   100%
models\truefalse_question.py            7      0   100%
services\question_timer.py             10      0   100%
services\quiz_service.py               53      0   100%
services\quiz_timer.py                 10      0   100%
services\scoring_service.py             7      0   100%
services\timed_input_service.py        20      0   100%
-------------------------------------------------------
TOTAL                                 677     23     97%
```

**Why 97% and not 100%?**

The 23 missed lines fall into two categories that cannot be covered by tests:

1. **`main.py` (18 lines)** — This is the entry-point script. It is meant to be run directly, not imported by a test. If a test imported `main.py`, it would actually start the quiz and wait for keyboard input, which is not suitable for automated testing. This is expected and intentional.

2. **Abstract `pass` bodies in the 3 interfaces (5 lines)** — In Python, when you declare an `@abstractmethod`, the body is a `pass` statement. This `pass` line is technically executable but can never actually be reached, because Python's ABC mechanism prevents any abstract class from being instantiated directly. These lines are structurally unreachable — no test can ever execute them.

All real business logic — every calculation, every branch, every conditional — is at **100% coverage**.

---

## 12. Sample Output

```
==================================================
  QUIZ STARTED
  Total time  : 60 seconds
  Per question: 20 seconds
  Marking     : Correct +10 | Wrong -5 | No answer 0
==================================================

[Question 1/3]   Quiz time left: 60s  |  This question: 20s

MCQ Question
Which language is used for AI?
1. Python
2. HTML
3. CSS
4. SQL
Your Answer: Python
✅  Correct!  [+10 marks]

[Question 2/3]   Quiz time left: 57s  |  This question: 20s

True/False Question
Python is statically typed.
Your Answer: true
❌  Wrong!  Correct answer was: false  [-5 marks]

[Question 3/3]   Quiz time left: 54s  |  This question: 20s

Fill in the Blank
___ is used for OOP in Python.
Your Answer:
⏰  Time's up!  Correct answer was: class  [+0 marks]

==================================================
  QUIZ COMPLETE
  Time taken  : 26.3s
  Correct     : 1  (+10 marks)
  Wrong       : 1  (-5 marks)
  No answer   : 1  (0 marks)
  Final Score : 5
==================================================
```
