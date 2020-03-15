

class Foo:
    CONSTANT = True

    @property
    def _bar(self):
        ...

    @property
    def bar(self):
        ...

    # It's ok with static methods
    @staticmethod
    def egg():
        ...

    @staticmethod
    def _egg():
        ...


    @classmethod
    def _foobar(cls):
        ...

    @classmethod
    def foobar(cls):
        ...
