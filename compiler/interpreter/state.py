from contextlib import contextmanager

class State:
    self = None
    stdout = None

    @classmethod
    @contextmanager
    def print(cls, value):
        if cls.stdout is None:
            cls.stdout = ""

        cls.stdout += str(value)

    @classmethod
    @contextmanager
    def selfScope(cls, self):
        previous_self = cls.self
        cls.self = self

        yield

        cls.self = previous_self
