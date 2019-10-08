from dateutil.parser import parse


class Type(object):
    none = 0
    categorical = 1
    numerical = 2
    cDate = 3


class Columns:
    def __init__(self):
        self.categorical = []
        self.date = []
        self.numerical = []


def columnType(data):
    if isNumber(data):
        return Type.numerical
    if isDate(data):
        return Type.cDate
    if isWord(data):
        return Type.categorical
    return Type.none


def isDate(field, fuzzy=False):
    field = str(field)
    try:
        parse(field, fuzzy=False)
        return True
    except ValueError:
        return False


def isNumber(s):
    try:
        complex(s)
    except ValueError:
        return False
    return True


def isWord(field):
    if not isinstance(field, str):
        return False
    return True
