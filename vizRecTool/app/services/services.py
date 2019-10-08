import csv
import itertools
import os
import pandas as pd
import altair as alt
import sys
from django.core.files.storage import FileSystemStorage

sys.path.append(".")
import sys

sys.path.append("..")
import utils


class FileData:
    FILE_FOLDER = 'files/'

    def loadData(csvFile):

        fileName = csvFile.name
        filePath = FileData.FILE_FOLDER + csvFile.name

        if not (fileName.lower().endswith('.csv')):
            raise Exception('Tipo de arquivo inválido. Insira um ".csv"')

        if not (os.path.isfile(filePath)):
            upload(csvFile)

        df = pd.read_csv(FileData.FILE_FOLDER + csvFile.name, nrows=5, index_col=False, encoding="ISO-8859-1",
                         quoting=True, engine='c')
        df = df.applymap(str)

        header = formatLine(df.columns[0:].values)
        line = formatLine(df.iloc[1].values)

        columns = categorizeColumns(line, header)
        categoricalColumns = columns.categorical
        categoricalColumns.extend(columns.date)
        numericalColumns = columns.numerical

        # print("Categorical: ", categoricalColumns, "Numerical:", numericalColumns)
        return categoricalColumns, numericalColumns


class Chart:

    def buildChart(csvFile, xAxis, yAxis):
        fileName = csvFile
        filePath = FileData.FILE_FOLDER + fileName
        fileName = fileName[:-4]

        df = pd.read_csv(filePath, index_col=False, encoding="ISO-8859-1", quoting=True, engine='c', error_bad_lines = False)
        df = cleanDataFrame(df)

        line = formatLine(df.iloc[1].values)
        header = formatLine(df.columns[0:].values)
        chartColumns = categorizeColumns(line, header)
        print(chartColumns.categorical)

        return df


def categorizeColumns(line, header):
    columns = utils.Columns()

    for i in range(len(line)):
        # print(line[i], " == ", utils.columnType(line[i]))

        if utils.columnType(line[i]) == utils.Type.categorical:
            columns.categorical.append(header[i].upper())
        elif utils.columnType(line[i]) == utils.Type.cDate:
            columns.date.append(header[i].upper())
        else:
            columns.numerical.append(header[i].upper())

    # print("Categorical columns: ", columns.categorical, "\n Quantitative columns: ", columns.numerical, "\n Date columns: ", columns.date)
    return columns


def cleanDataFrame(df):
    df = df.apply(lambda x: x.str.strip("'"))
    df.columns = df.columns.str.replace("'", '')
    df.columns = df.columns.str.replace('"', '')
    return df


def upload(file):
    folder = 'files/'
    fs = FileSystemStorage(location=folder)  # defaults to   MEDIA_ROOT
    filename = fs.save(file.name, file)
    file_url = fs.url(filename)
    return file_url


def formatLine(line):
    line = ''.join(line)
    delimiter = detectDelimiter(line)

    formattedLine = line.replace('"', '').replace("'", "").split(delimiter)
    formattedLine = formattedLine[0:]
    return formattedLine


def detectDelimiter(csvFile):
    if csvFile.find(";") != -1:
        return ";"
    if csvFile.find(",") != -1:
        return ","
    # default delimiter (MS Office export)
    return ";"
