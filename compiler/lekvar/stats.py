
class Stats:
    __attrs__ = ['static', 'forward']

    static = False
    forward = False

    def __init__(self, parent):
        if parent is not None:
            if parent.stats.static_transitive:
                self.static = parent.stats.static

            if parent.stats.forward_transitive:
                self.forward = parent.stats.forward

    def __repr__(self):
        results = []
        for attr in self.__attrs__:
            results.append("{}: {}".format(attr, getattr(self, attr)))
        return "{{}}".format(", ".join(results))

class SoftScopeStats(Stats):
    __attrs__ = Stats.__attrs__ + ['definitely_returns', 'might_return']

    definitely_returns = False
    might_return = False

    def merge(self, other):
        self.definitely_returns = self.definitely_returns and other.definitely_returns
        self.might_return = self.definitely_returns or other.definitely_returns

    def update(self, other):
        self.definitely_returns = self.definitely_returns or other.definitely_returns
        self.might_return = self.definitely_returns or other.definitely_returns

class ScopeStats(SoftScopeStats):
    __attrs__ = SoftScopeStats.__attrs__ + ['static_transitive', 'forward_transitive']

    static_transitive = True
    forward_transitive = True
