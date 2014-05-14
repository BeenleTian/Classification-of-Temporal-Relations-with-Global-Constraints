class RelationType:
    BEFORE = 0
    IS_INCLUDED = 1
    AFTER = 2
    INCLUDES = 3
    ENDS = 4
    ENDED_BY = 5
    IBEFORE = 6
    IAFTER = 7
    SIMULTANEOUS = 8
    BEGINS = 9
    BEGUN_BY = 10
    DURING = 11
    DURING_INV = 12
    UNKNOWN = 13

    @classmethod
    def get_id(cls, text):
        if text == "BEFORE":
            return cls.BEFORE
        elif text == "IS_INCLUDED":
            return cls.IS_INCLUDED
        elif text == "INCLUDES":
            return cls.INCLUDES
        elif text == "AFTER":
            return cls.AFTER
        elif text == "ENDS":
            return cls.ENDS
        elif text == "ENDED_BY":
            return cls.ENDED_BY
        elif text == "IBEFORE":
            return cls.IBEFORE
        elif text == "IAFTER":
            return cls.IAFTER
        elif text == "BEGINS":
            return cls.BEGINS
        elif text == "BEGUN_BY":
            return cls.BEGUN_BY
        elif text == "DURING":
            return cls.DURING
        elif text == "DURING_INV":
            return cls.DURING_INV
        elif text == "SIMULTANEOUS":
            return cls.SIMULTANEOUS
        else:
            return cls.UNKNOWN
