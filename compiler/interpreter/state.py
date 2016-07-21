from contextlib import contextmanager

class State:
    self = None
    stdout = None

    @classmethod
    @contextmanager
    def print(self, value):
        if self.stdout is None:
            self.stdout = ""

        self.stdout += str(value) + "\n"

    @classmethod
    @contextmanager
    def selfScope(self, value):
        previous_self = self.self
        self.self = value

        yield

        self.self = previous_self
