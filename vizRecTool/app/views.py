# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import TemplateView
from django.shortcuts import render, render_to_response
from services.services import FileData
from services.services import Chart
from vega_datasets import data
import altair as alt
import pandas as pd
import forms



class IndexView(TemplateView):
    template_name = 'index.html'

    def file(request):

        if request.method == 'POST':
            csvFile = request.FILES['csvfile']

            try:
                catData, quantData = FileData.loadData(csvFile)
                context = {
                    'categoricalData': catData,
                    'quantitativeData': quantData,
                    'filePath': csvFile.name
                }
            except Exception as e:
                print(e)
                return render(request, IndexView.template_name, messages.error(request, "Erro ao carregar arquivo"))

            return render(request, IndexView.template_name, context)

    def chart(request):
        form = forms.fileForm(request.POST or None)
        quantitative = request.POST.getlist('quantitativeData')[0]
        categorical = request.POST.getlist('categoricalData')[0]

        if form.is_valid():
            xAxis = form.cleaned_data['selectedX']
            yAxis = form.cleaned_data['selectedY']

        try:
            file = request.POST.get('fileBtn', False)
            if not (xAxis and yAxis and file):
                print("X:", xAxis, "Y:", yAxis, "File:", file)
                raise Exception('Variável X ou Y não recebida')

            csvFile = request.POST.get("fileBtn")
            resultChart = Chart.buildChart(csvFile, xAxis, yAxis)
            print('TAMANHO', resultChart)
            context = locals()
            context = {
                'chart': resultChart,
                'quantitativeData': eval('[' + context['quantitative'] + ']')[0],
                'categoricalData': eval('[' + context['categorical'] + ']')[0],
                'filePath': file,
            }

            #print("context: ", context)
        except Exception as e:
            print("Exception", e)
            return render(request, IndexView.template_name, messages.error(request, "Erro ao gerar gráfico"))

        return render(request, IndexView.template_name, context)


class Type(object):
    bar = 0
    line = 1
    scatter = 2
    pie = 3
