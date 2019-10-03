import csv
import itertools
import pandas as pd
import altair as alt
import sys

sys.path.append(".")
import sys

sys.path.append("..")
import utils


class FileDataService:

    def loadData(csvFile):

        fileName = csvFile.name
        if not (fileName.lower().endswith('.csv')):
            return False
        fileName = fileName[:-4]

        df = pd.read_csv(csvFile, nrows=20, index_col=False, encoding="ISO-8859-1", quoting=True)
        df = df.applymap(str)

        header = formatLine(df.columns[0:].values)
        print("Header", header)
        line = formatLine(df.iloc[1].values)
        categoricalColumns = []
        numericalColumns = []

        for i in range(len(line)):
            print(line[i], " == ", utils.columnType(line[i]))
            if (utils.columnType(line[i]) == utils.Type.categorical) or (utils.columnType(line[i]) == utils.Type.cDate):
                categoricalColumns.append(header[i].upper())
            else:
                numericalColumns.append(header[i].upper())
        print("Categorical columns: ", categoricalColumns, "\n Quantitative columns: ", numericalColumns)

        return categoricalColumns, numericalColumns


def findFileHeader(fileName):
    with open(fileName) as file:

        reader = csv.reader(file)
        user_header = next(reader)  # Add this line if there the header is

        for row in reader:
            if any(row):  # Pick up the non-blank row of list
                print(row)  # Just for verification
                (next(itertools.islice(csv.reader(file), None)))


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
