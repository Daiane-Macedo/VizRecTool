# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import render
from django.views.generic import TemplateView

import forms
from services.services import Chart
from services.services import FileData
import logging


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
                return render(request, IndexView.template_name, messages.error(request, e))

            return render(request, IndexView.template_name, context)

    def chart(request):
        form = forms.fileForm(request.POST or None)
        quantitative = request.POST.getlist('quantitativeData')[0]
        categorical = request.POST.getlist('categoricalData')[0]
        resultChart = None
        context = locals()
        if form.is_valid():
            xAxis = form.cleaned_data['selectedX']
            yAxis = form.cleaned_data['selectedY']

        try:
            file = request.POST.get('fileBtn', False)
            if not (xAxis and yAxis and file):
                # print("X:", xAxis, "Y:", yAxis, "File:", file)
                return render(request, IndexView.template_name, messages.error(request, "Erro ao gerar gráfico"))

            csvFile = request.POST.get("fileBtn")
            resultChart = Chart.build_chart(csvFile, xAxis, yAxis)
            myform = form.full_clean()

            context = {
                'charts': resultChart,
                'quantitativeData': eval('[' + context['quantitative'] + ']')[0],
                'categoricalData': eval('[' + context['categorical'] + ']')[0],
                'filePath': file,
                'selectedValueX': xAxis,
                'selectedValueY': yAxis,
                'fileForm': myform
            }

        except Exception as ex:
            logging.exception(ex)
            context = {
                'quantitativeData': eval('[' + context['quantitative'] + ']')[0],
                'categoricalData': eval('[' + context['categorical'] + ']')[0],
                'filePath': file,
                'selectedValueX': xAxis,
                'selectedValueY': yAxis
            }
            return render(request, IndexView.template_name, context, messages.error(request, "Erro ao gerar gráfico"))

        return render(request, IndexView.template_name, context)


class Type(object):
    bar = 0
    line = 1
    scatter = 2
    pie = 3
