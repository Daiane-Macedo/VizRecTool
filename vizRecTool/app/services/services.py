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
        print(df.columns)
        print(df.iloc[0:10, 0:10])

        grouped_df = df.groupby(['ÓRGÃO SUPERIOR'])
        print(grouped_df.first())

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
    pie = 1
    bar = 2
    columns = 2
    line = 3

    def buildChart(csvFile, xAxis, yAxis):
        chart = None
        chartsList = []
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
            data = [go.Bar(
                x=df[xAxis],
                y=df[yAxis],
                showlegend=True, name=yAxis
            )]
            layout = getLayout(xAxis, yAxis, fileName)
            figure = go.Figure(data=data, layout=layout)
            chart = opy.plot(figure, auto_open=False, output_type='div')

            return chart

        if xAxis in col.date and yAxis in col.quantitative:  # line

            for category in col.categorical:
                trace = go.Scatter(marker=dict(symbol='circle'),
                                   mode='lines+markers',
                                   showlegend=True,
                                   name=yAxis)
                layout = getLayout(xAxis, yAxis, fileName)
                figure = go.Figure(data=trace, layout=layout)

                for name, group in df.groupby(category):
                    trace.name = name
                    trace.y = group[yAxis]
                    trace.x = df[xAxis]
                    figure.add_trace(trace)

                chart = opy.plot(figure, auto_open=False, output_type='div')
                chartsList.append(chart)
            return chart

        if xAxis in col.quantitative and yAxis in col.quantitative:  # scatter plot
            trace1 = go.Scatter(x=df[xAxis], y=df[yAxis],
                                marker=dict(symbol='circle'),
                                mode='markers',
                                line=dict(color='rgb(255,0,0)'), showlegend=True, name=yAxis)
            data = [trace1]
            layout = getLayout(xAxis, yAxis, fileName)
            figure = go.Figure(data=data, layout=layout)
            chart = opy.plot(figure, auto_open=False, output_type='div')

        return chart


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
