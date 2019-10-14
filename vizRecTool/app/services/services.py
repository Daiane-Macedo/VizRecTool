from django.core.files.storage import FileSystemStorage
import os
import pandas as pd
import altair as alt
import sys

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

        delimiter = detectDelimiter(filePath)
        df = pd.read_csv(filePath, nrows=5, index_col=False, encoding='utf-8',
                         sep=delimiter)
        df = cleanDataFrame(df)
        df.columns = map(str.upper, df.columns)

        header = df.columns.values
        line = df.iloc[1].values
        columns = categorizeColumns(line, header)
        quantitativeColumns = columns.quantitative
        categoricalColumns = columns.categorical
        categoricalColumns.extend(columns.date)
        # categoricalColumns.extend(columns.quantitative)

        print("Categorical: ", categoricalColumns, "Numerical:", quantitativeColumns)
        return categoricalColumns, quantitativeColumns


class Chart:
    pie = 1
    bar = 2
    columns = 2
    line = 3

    def buildChart(csvFile, xAxis, yAxis):
        chart = None
        fileName = csvFile
        filePath = FileData.FILE_FOLDER + fileName
        fileName = fileName[:-4]

        delimiter = detectDelimiter(filePath)
        df = pd.read_csv(filePath, index_col=False, encoding='utf-8', nrows=4999, sep=delimiter)
        df = cleanDataFrame(df)
        df.columns = map(str.upper, df.columns)
        header = df.columns.values
        line = df.iloc[1].values
        col = categorizeColumns(line, header)
        df = parse_columns(df, col)

        if xAxis in col.categorical and yAxis in col.quantitative:  # bar
            chart = alt.Chart(df, title=fileName).mark_bar().encode(
                x=xAxis,
                y=yAxis
            ).interactive().properties(
                width=600,
                height=300
            )
        if xAxis in col.date and yAxis in col.quantitative:  # line
            chart = alt.Chart(df, title=fileName).mark_line().encode(
                x=xAxis,
                y=yAxis
            ).interactive().properties(
                width=600,
                height=300
            )

        if xAxis in col.quantitative and yAxis in col.quantitative:  # scatter plot
            chart = alt.Chart(df, title=fileName).mark_circle().encode(
                x=xAxis,
                y=yAxis
            ).interactive()

        return chart


def parse_columns(df, col):
    for date in col.date:
        df[date] = pd.to_datetime(df[date])

    for quant in col.quantitative:
        if (df[quant].str.contains(",", regex=False)).any():
            df[quant] = df[quant].apply(lambda x: float(x.replace(".", "").replace(",", ".")))
    return df


def categorizeColumns(line, header):
    columns = utils.Columns()

    for i in range(len(line)):
        print(line[i])
        if utils.columnType(line[i]) == utils.Type.categorical:
            columns.categorical.append(header[i].upper())
        elif utils.columnType(line[i]) == utils.Type.cDate:
            columns.date.append(header[i].upper())
        else:
            columns.quantitative.append(header[i].upper())

    # print("Categorical columns: ", columns.categorical, "\n Quantitative columns: ", columns.numerical, "\n Date columns: ", columns.date)
    return columns


def cleanDataFrame(df):
    df = df.replace({'\'': '"'}, regex=True)
    df = df.applymap(str)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # df = df.apply(lambda x: x.str.strip("'"))
    # df.columns = df.columns.str.replace("'", '')
    # df.columns = df.columns.str.replace('"', '')
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
    # formattedLine = formattedLine[0:]
    print("retorno", formattedLine)

    return formattedLine


def detectDelimiter(csvFile):
    with open(csvFile, 'r', encoding="ISO-8859-1") as myCsvfile:
        header = myCsvfile.readline()
        if header.find(";") != -1:
            return ";"
        if header.find(",") != -1:
            return ","
    # default delimiter (MS Office export)
    return ";"
