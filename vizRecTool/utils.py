import re

from dateutil.parser import parse
from django import forms


class Type(object):
    none = 0
    categorical = 1
    numerical = 2
    cDate = 3

class Columns:
    def __init__(self):
        self.categorical = []
        self.date = []
        self.quantitative = []

class fileForm(forms.Form):
    selectedY: forms.CharField()
    selectedX: forms.CharField()
    selectColumn: forms.CharField()

def columnType(data):
    data = str(data).strip()
    regNumber = re.compile(r"(\d),(\d)")  # looks for numbers with commas
    if regNumber.search(data) or isNumber(data):
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
