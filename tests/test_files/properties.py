class Foo:
    def __str__(self):
        ...

    @property
    def bar(self):
        ...

    @bar.setter
    def bar(self, value):
        ...

    @bar.deleter
    def bar(self):
        ...

    @property
    def _bar(self):
        ...

    @_bar.setter
    def _bar(self, value):
        ...

    @_bar.deleter
    def _bar(self):
        ...

    @property
    def __bar(self):
        ...

    @__bar.setter
    def __bar(self, value):
        ...

    @__bar.deleter
    def __bar(self):
        ...

    @staticmethod
    def _egg():
        ...

