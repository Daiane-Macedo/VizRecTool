from dateutil.parser import parse


class Type(object):
    none = 0
    categorical = 1
    numerical = 2
    cDate = 3


def columnType(data):
    if isDate(data):
        return Type.cDate
    if isNumber:
        return Type.numerical
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
        complex(s)  # for int, long, float and complex
    except ValueError:
        return False
    return True


def isWord(field):
    if field and field.strip():
        return False
    return True
