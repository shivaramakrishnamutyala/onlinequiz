import pytest
from unittest.mock import patch
from services.timed_input_service import TimedInputService

class TestTimedInputService:

    def test_stores_timeout(self):
        svc = TimedInputService(timeout_seconds=5.0)
        assert svc._timeout == 5.0

    def test_stores_custom_timeout(self):
        svc = TimedInputService(timeout_seconds=0.5)
        assert svc._timeout == 0.5

    def test_returns_answer_when_input_given(self):
        """Patch builtins.input to return immediately with a value."""
        svc = TimedInputService(timeout_seconds=5.0)
        with patch("builtins.input", return_value="Python"):
            result = svc.get_input("Answer: ")
        assert result == "Python"

    def test_returns_empty_string_when_user_submits_empty(self):
        svc = TimedInputService(timeout_seconds=5.0)
        with patch("builtins.input", return_value=""):
            result = svc.get_input("Answer: ")
        assert result == ""

    def test_returns_whitespace_answer_unchanged(self):
        svc = TimedInputService(timeout_seconds=5.0)
        with patch("builtins.input", return_value="  hello  "):
            result = svc.get_input("Answer: ")
        assert result == "  hello  "

    def test_returns_none_on_timeout(self, capsys):
        """Use a very short timeout and no mocked input so it times out."""
        svc = TimedInputService(timeout_seconds=0.05)
        import threading
        block = threading.Event()

        def _blocking_input(_prompt):
            block.wait()  
            return "late"

        with patch("builtins.input", side_effect=_blocking_input):
            result = svc.get_input("Answer: ")

        block.set()        
        assert result is None

    def test_prints_newline_on_timeout(self, capsys):
        """A newline must be printed when time runs out."""
        import threading
        block = threading.Event()

        def _blocking_input(_prompt):
            block.wait()
            return "late"

        svc = TimedInputService(timeout_seconds=0.05)
        with patch("builtins.input", side_effect=_blocking_input):
            svc.get_input("Answer: ")

        block.set()
        captured = capsys.readouterr().out
        assert "\n" in captured

    def test_returns_none_on_eof_error(self):
        """EOFError (e.g. piped input exhausted) must be handled gracefully."""
        svc = TimedInputService(timeout_seconds=5.0)
        with patch("builtins.input", side_effect=EOFError):
            result = svc.get_input("Answer: ")
        assert result is None
