import csv
import itertools
import re
import pandas as pd
import altair as alt
import sys

sys.path.append(".")
import sys

sys.path.append("..")
import utils


class GraphService:

    def buildGraph(csvFile):
        fileName = csvFile.name
        if fileName.lower().endswith('.csv'):
            fileName = fileName[:-4]

        df = pd.read_csv(csvFile, nrows=25)
        df = df.reset_index()
        columns = formatLine(df.columns[0])
        row = df.loc[0, :].values
        for x in row:
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
    delimiter = detectDelimiter(line)
    formattedLine = line.replace('"', '').replace("'", "").split(delimiter)
    return formattedLine


def detectDelimiter(csvFile):
    if csvFile.find(";") != -1:
        return ";"
    if csvFile.find(",") != -1:
        return ","
    # default delimiter (MS Office export)
    return ";"
