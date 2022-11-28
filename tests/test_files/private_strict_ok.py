class Foo:
    CONSTANT = True

    @property
    def _bar(self):
        ...

    @property
    def __bar(self):
        ...

    @staticmethod
    def _egg():
        ...

    @staticmethod
    def __egg():
        ...

    @classmethod
    def foobar(cls):
        ...

    @classmethod
    def __foobar(cls):
        ...