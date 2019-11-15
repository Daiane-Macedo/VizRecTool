import re

import chardet
import pandas as pd
from dateutil.parser import parse
from django import forms
from django.core.files.storage import FileSystemStorage


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


def parse_columns(df, col):
    for date in col.date:
        df[date] = pd.to_datetime(df[date])

    for quant in col.quantitative:
        if (df[quant].str.contains(",", regex=False)).any():
            df[quant] = df[quant].apply(lambda x: (x.replace(".", "").replace(",", ".")))
    return df


def clean_dataFrame(df):
    try:
        df = df.str.replace({'\'': '"'}, regex=True)
    except Exception as e:
        print(e)
    df = df.applymap(str)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df


def detect_encode(csvFile):
    with open(csvFile, 'rb') as f:
        encode = chardet.detect(f.read())  # or readline if the file is large
        return encode


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


def format_line(line):
    line = ''.join(line)
    delimiter = detect_delimiter(line)
    formattedLine = line.replace('"', '').replace("'", "").split(delimiter)
    # formattedLine = formattedLine[0:]
    print("retorno", formattedLine)

    return formattedLine


def detect_delimiter(csvFile, encode):
    with open(csvFile, 'r', encoding=encode['encoding']) as myCsvfile:
        header = myCsvfile.readline()
        if header.find(";") != -1:
            return ";"
        if header.find(",") != -1:
            return ","
    # default delimiter (MS Office export)
    return ";"


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


def upload(file):
    folder = 'files/'
    fs = FileSystemStorage(location=folder)  # defaults to   MEDIA_ROOT
    filename = fs.save(file.name, file)
    file_url = fs.url(filename)
    return file_url
