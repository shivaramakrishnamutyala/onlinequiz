import threading
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
