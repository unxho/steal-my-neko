class VerifiedList(list):
    """
    Custom list class but with ability to show
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
