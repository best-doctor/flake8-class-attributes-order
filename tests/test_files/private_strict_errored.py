class Foo:
    CONSTANT = True

    @property
    def __bar(self):
        ...

    @property
    def _bar(self):
        ...

    # It's ok with static methods
    @staticmethod
    def __egg():
        ...

    @staticmethod
    def _egg():
        ...


    @classmethod
    def __foobar(cls):
        ...

    @classmethod
    def foobar(cls):
        ...
