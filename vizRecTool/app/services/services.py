import os
import pandas as pd
import altair as alt
import sys
import plotly.offline as opy
import plotly.graph_objs as go

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
            utils.upload(csvFile)

        encode = utils.detect_encode(filePath)
        delimiter = utils.detect_delimiter(filePath, encode)

        df = pd.read_csv(filePath, nrows=50, index_col=False, encoding=encode['encoding'],
                         sep=delimiter)
        df = utils.clean_dataFrame(df)
        df.columns = map(str.upper, df.columns)
        header = df.columns.values
        line = df.iloc[1].values
        columns = categorize_columns(line, header)

        quantitativeColumns = columns.quantitative
        categoricalColumns = columns.categorical
        categoricalColumns.extend(columns.date)
        categoricalColumns.extend(columns.quantitative)

        print("Categorical: ", categoricalColumns, "Numerical:", quantitativeColumns)
        return categoricalColumns, quantitativeColumns


class Chart:
    def __init__(self):
        self.figure = None
        self.content = None

    def build_chart(csvFile, xAxis, yAxis):
        # chartsList = []
        fileName = csvFile
        filePath = FileData.FILE_FOLDER + fileName
        fileName = fileName[:-4]

        encode = utils.detect_encode(filePath)
        delimiter = utils.detect_delimiter(filePath, encode)

        df = pd.read_csv(filePath, index_col=False, encoding=encode['encoding'], nrows=4999, sep=delimiter)
        df = utils.clean_dataFrame(df)
        df.columns = map(str.upper, df.columns)
        header = df.columns.values
        line = df.iloc[1].values
        col = categorize_columns(line, header)
        df = utils.parse_columns(df, col)

        if xAxis in col.categorical and yAxis in col.quantitative:  # bar
            chartsList = build_bar_chart(df, xAxis, yAxis, fileName)
            return chartsList

        if xAxis in col.date and yAxis in col.quantitative:  # line
            chartsList = []
            for category in col.categorical:
                chart = build_line_chart(df, category, xAxis, yAxis, fileName)
                chartsList.append(chart)

            # truncate list in 5 charts (max)
            chartsList = chartsList[0: 5]
            return chartsList

        if xAxis in col.quantitative and yAxis in col.quantitative:  # scatter plot
            chartsList = build_scatter_plot(df, xAxis, yAxis, fileName)
            return chartsList


def build_line_chart(dataframe, category, xAxis, yAxis, chartName):
    df = dataframe.copy()
    chartsList = []
    trace = go.Scatter(marker=dict(symbol='circle'),
                       mode='lines+markers',
                       showlegend=True,
                       name=yAxis)
    layout = getLayout(xAxis, yAxis, chartName)
    figure = go.Figure(data=trace, layout=layout)

    for name, group in df.groupby(category):
        print(category)
        trace.name = name
        trace.y = group[yAxis]
        trace.x = df[xAxis]
        figure.add_trace(trace)
    chart = Chart()
    chart.content = opy.plot(figure, auto_open=False, output_type='div')
    return chart


def build_bar_chart(df, xAxis, yAxis, chartName):
    chartsList = []
    data = [go.Bar(
        x=df[xAxis],
        y=df[yAxis],
        showlegend=True, name=yAxis
    )]
    layout = getLayout(xAxis, yAxis, chartName)
    figure = go.Figure(data=data, layout=layout)
    chart = Chart()
    chart.content = opy.plot(figure, auto_open=False, output_type='div')
    chartsList.append(chart)
    # truncate list in 5 charts (max)
    chartsList = chartsList[0: 5]
    return chartsList


def build_scatter_plot(df, xAxis, yAxis, chartName):
    chartsList = []
    trace1 = go.Scatter(x=df[xAxis], y=df[yAxis],
                        marker=dict(symbol='circle'),
                        mode='markers',
                        line=dict(color='rgb(255,0,0)'), showlegend=True, name=yAxis)
    data = [trace1]
    layout = getLayout(xAxis, yAxis, chartName)
    figure = go.Figure(data=data, layout=layout)
    chart = Chart()
    chart.content = opy.plot(figure, auto_open=False, output_type='div')
    chartsList.append(chart)

    return chartsList


def categorize_columns(line, header):
    columns = utils.Columns()

    for i in range(len(line)):
        if utils.columnType(line[i]) == utils.Type.categorical:
            columns.categorical.append(header[i].upper())
        elif utils.columnType(line[i]) == utils.Type.cDate:
            columns.date.append(header[i].upper())
        else:
            columns.quantitative.append(header[i].upper())

    # print("Categorical columns: ", columns.categorical, "\n Quantitative columns: ", columns.numerical, "\n Date columns: ", columns.date)
    return columns


def getLayout(xAxis, yAxis, name):
    layout = go.Layout(
        title=name,
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(text=xAxis),
            autorange=True, ticks='', showgrid=False, zeroline=False
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(text=yAxis),
            autorange=True, ticks='', zeroline=False, tickformat=None
        )
    )
    return layout
