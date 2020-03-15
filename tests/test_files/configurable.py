

class Foo:
    CONSTANT = 42

    field = 17

    class Meta:
        a = 3

    def __init__(self):
        ...

    @property
    def _egg(self):
        ...

    @property
    def egg(self):
        ...

    def bar(self):
        ...

    def _bar(self):
        ...

    def __str__(self):
        ...
