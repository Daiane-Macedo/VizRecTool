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
            return True

        fileName = fileName[:-4]

        df = pd.read_csv(csvFile, nrows=25, encoding="ISO-8859-1")
        df = df.reset_index()
        df = df.applymap(str)
        print(df)
        columns = formatLine(df.columns[1:].values)
        line = formatLine(df.loc[0, :].values)
        # row = df.loc[0, :].values

        for x in line:
            print(x)
            print(utils.columnType(x))

        return None


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
