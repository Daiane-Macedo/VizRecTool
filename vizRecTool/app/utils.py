from datetime import datetime
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


def data_binning(df, xAxis, yAxis, category):
    hasMonth = True
    months = []
    # Verifying if date has month
    try:
        months = df[xAxis].dt.month.unique()
    except Exception:
        hasMonth = False

    minTime = min(df[xAxis])
    maxTime = max(df[xAxis])
    minYear = minTime.year
    maxYear = maxTime.year

    if hasMonth:
        minMonth = min(months)
        maxMonth = max(months)
    yearsQty = maxYear - minYear + 1

    # if has only year field or more than 5 distinct years: interval = year
    if not hasMonth or minYear != maxYear and yearsQty > 5:
        print("Binning by YEAR...")
        df[xAxis] = df[xAxis].map(lambda x: str(x.year))

    else:
        # if has more than one month in date column: interval = month
        if minMonth != maxMonth:
            print('Binning by MONTH...')
            df[xAxis] = df[xAxis].map(
                lambda x: str(x.year) + "-" +
                          (str(x.month) if len(str(x.month)) == 2 else '0' + str(
                              x.month)))  # add 0 to month number if is 1, 2, 3...9
            print('Grouped by month', df)
        else:
            print('Grouped by day', df)

    # sum by quantitative column
    if category:
        df = df.groupby([xAxis, category], as_index=False)[yAxis].sum()
    else:
        df = df.groupby([xAxis], as_index=False)[yAxis].sum()
    return df


def parse_columns(df, col):
    for date in col.date:
        df[date] = parse_date(df[date])
        df = df.sort_values(by=date)

    for quant in col.quantitative:
        # replace delimiter
        if (df[quant].str.contains(",", regex=False)).any():
            df[quant] = df[quant].apply(lambda x: (x.replace(".", "").replace(",", ".")))
        # convert to numeric
        df[quant] = pd.to_numeric(df[quant], errors='coerce')

    return df


def parse_date(dfColumn):
    dates = dfColumn.unique()
    dt = next((el for el in dates if el is not None), None)  # get first non-null item in date's list
    dayFirst = True

    # verifying if date is in YYYY/MM/DD format
    format_list = ['%Y-%m-%d', '%Y-%b-%d']
    for date_format in format_list:
        try:
            datetime.strptime(dt, date_format)
            dayFirst = False
            break
        except ValueError:
            continue

    parsedDf = lookup(dfColumn, dayFirst)
    return parsedDf


def lookup(s, dFormat):
    """
    This is an extremely fast approach to datetime parsing.
    For large data, the same dates are often repeated. Rather than
    re-parse these, we store all unique dates, parse them, and
    use a lookup to convert all dates.
    """
    dates = {date: pd.to_datetime(date, dayfirst=dFormat) for date in s.unique()}
    return s.map(dates)


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
        encode = chardet.detect(f.readline())
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


def upload(path, file):
    fs = FileSystemStorage(location=path)
    filename = fs.save(file.name, file)
    file_url = fs.url(filename)
    return file_url
