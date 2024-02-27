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

    @property
    def __foo(self):
        pass

    @classmethod
    def foobar(cls):
        pass

    @classmethod
    def __foobar(cls):
        pass

    def _barfoo(self):
        pass

    def __barfoo(self):
        pass
