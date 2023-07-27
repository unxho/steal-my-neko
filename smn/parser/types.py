from typing import Iterable, Optional


class VerifiedList(list):
    """
    Custom list class with ability to show
    if its objects are verified.
    """

    def __setitem__(self, *args):
        for i in args:
            if not hasattr(i, "verified"):
                raise TypeError("Type is unverifiable.")
        super().__setitem__(*args)

    @property
    def verified(self) -> bool:
        for i in self:
            if not i.verified:
                return False
        return True


class Parsers(list):
    def __init__(self, data: Iterable, weights: Optional[Iterable] = None):
        self.weights = list(weights) if weights is not None else None
        return super().__init__(data)

    def __delitem__(self, __key):
        if self.weights:
            self.weights.__delitem__(__key)
        return super().__delitem__(__key)
