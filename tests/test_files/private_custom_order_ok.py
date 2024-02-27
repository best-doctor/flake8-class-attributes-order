class Foo:
    CONSTANT = True

    def __init__(self):
        pass

    def __eq__(self, other):
        super(Foo, self).__eq__(other)

    @property
    def foo(self):
        pass

    @property
    def _foo(self):
        pass

    @classmethod
    def _foobar2(cls):
        pass

    def _barfoo(self):
        pass

    @property
    def __foo(self):
        pass

    @classmethod
    def __foobar(cls):
        pass

    def __barfoo(self):
        pass
