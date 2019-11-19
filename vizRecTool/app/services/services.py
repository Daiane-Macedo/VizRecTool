import os
import shutil
import sys
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as opy
import utils

sys.path.append("..")


class FileData:
    FILE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "files/")

    def loadData(csvFile):
        fileName = csvFile.name
        filePath = FileData.FILE_FOLDER + csvFile.name

        if not (fileName.lower().endswith('.csv')):
            raise Exception('Tipo de arquivo inválido. Insira um ".csv"')

        # cleaning old files and uploading received file
        shutil.rmtree(FileData.FILE_FOLDER)
        utils.upload(FileData.FILE_FOLDER, csvFile)

        encode = utils.detect_encode(filePath)
        delimiter = utils.detect_delimiter(filePath, encode)

        df = pd.read_csv(filePath, index_col=False, encoding=encode['encoding'],
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

        uniqueVal = df[xAxis].unique()
        if xAxis in col.categorical and yAxis in col.quantitative and len(uniqueVal) < 3:  # pie
            chartsList = []
            pie_chart = build_pie_chart(df, xAxis, yAxis, fileName)
            chartsList.append(pie_chart)
            bar_chart = build_bar_chart(df, xAxis, yAxis, fileName)
            chartsList.append(bar_chart)
            # def generate_tumbnail_images
            return chartsList

        if xAxis in col.categorical and yAxis in col.quantitative:  # bar
            chartsList = []
            bar_chart = build_bar_chart(df, xAxis, yAxis, fileName)
            chartsList.append(bar_chart)
            return chartsList

        if xAxis in col.date and yAxis in col.quantitative:  # line
            chartsList = []

            if not col.categorical:
                chart = build_line_chart(df, None, xAxis, yAxis, fileName)
                chartsList.append(chart)
            else:
                for category in col.categorical:
                    chart = build_line_chart(df, category, xAxis, yAxis, fileName)
                    chartsList.append(chart)

            # truncate list in 5 charts (max)
            chartsList = chartsList[0: 5]
            return chartsList

        if xAxis in col.quantitative and yAxis in col.quantitative:  # scatter plot
            chartsList = []
            if not col.categorical:
                chart = build_scatter_plot(df, None, xAxis, yAxis, fileName)
                chartsList.append(chart)
                # truncate list in 5 charts (max)
                chartsList = chartsList[0: 5]
            else:
                for category in col.categorical:
                    chart = build_scatter_plot(df, category, xAxis, yAxis, fileName)
                    chartsList.append(chart)
            return chartsList


def build_line_chart(dataframe, category, xAxis, yAxis, chartName):
    # format chart layout
    trace = go.Scatter(marker=dict(symbol='circle'),
                       mode='lines+markers',
                       showlegend=True,
                       name=yAxis)
    layout = getLayout(xAxis, yAxis, chartName)
    figure = go.Figure(data=trace, layout=layout)

    # group by and sum numeric values
    if category:
        dataframe = dataframe[[category, yAxis, xAxis]]
        df = utils.data_binning(dataframe, xAxis, yAxis, category)
        # df = dataframe.groupby([xAxis, category], as_index=False)[yAxis].sum()

        # add traces to chart
        unique = df[category].unique()
        for name in unique:
            df2 = dict(tuple(df.groupby(category)))
            df2 = df2[name]
            trace.name = name
            trace.y = df2[yAxis]
            trace.x = df2[xAxis]
            figure.add_trace(trace)
    else:
        dataframe = dataframe[[yAxis, xAxis]]
        df = utils.data_binning(dataframe, xAxis, yAxis, None)
        trace.name = yAxis
        trace.y = df[yAxis]
        trace.x = df[xAxis]
        figure.add_trace(trace)

    chart = Chart()
    chart.content = opy.plot(figure, auto_open=False, output_type='div')
    return chart


def build_bar_chart(dataframe, xAxis, yAxis, chartName):
    trace = go.Bar(showlegend=True)
    layout = getLayout(xAxis, yAxis, chartName)
    figure = go.Figure(data=trace, layout=layout)
    df = dataframe[[yAxis, xAxis]]

    # add traces to chart
    unique = df[xAxis].unique()
    df = dataframe.groupby([xAxis], as_index=False)[yAxis].sum()
    for name in unique:
        df2 = dict(tuple(df.groupby(xAxis)))
        df2 = df2[name]
        trace.name = name
        trace.y = df2[yAxis]
        trace.x = df2[xAxis]
        figure.add_trace(trace)

    chart = Chart()
    chart.content = opy.plot(figure, auto_open=False, output_type='div')
    return chart


def build_pie_chart(df, labels, values, fileName):
    data = [go.Pie(
        labels=df[labels],
        values=df[values],
        showlegend=True, name=labels
    )]
    figure = go.Figure(data)
    figure.update_layout(title_text=fileName)
    chart = Chart()
    chart.content = opy.plot(figure, auto_open=False, output_type='div')

    return chart


def build_scatter_plot(dataframe, category, xAxis, yAxis, chartName):
    trace = go.Scatter(marker=dict(symbol='circle'), mode='markers', showlegend=False)
    layout = getLayout(xAxis, yAxis, chartName)
    figure = go.Figure(data=trace, layout=layout)

    if category:
        figure.update_layout(title=chartName + ' ( ' + (category.lower()) + ')')
        df = dataframe[[category, yAxis, xAxis]]
        figure.update_layout(showlegend=True)

        # add categories to chart
        unique = df[category].unique()
        for name in unique:
            df2 = dict(tuple(df.groupby(category)))
            df2 = df2[name]
            trace.name = name
            trace.y = df2[yAxis]
            trace.x = df2[xAxis]
            figure.add_trace(trace)
    # No categories: build simple scatter plot
    else:
        trace.y = dataframe[yAxis]
        trace.x = dataframe[xAxis]
        figure.add_trace(trace)

    chart = Chart()
    chart.content = opy.plot(figure, auto_open=False, output_type='div')
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
