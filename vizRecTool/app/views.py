# -*- coding: utf-8 -*-
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import TemplateView
from django.shortcuts import render, render_to_response
from services.services import FileDataService
from django.contrib.staticfiles.views import serve
from vega_datasets import data
import altair as alt
import pandas as pd


class IndexView(TemplateView):
    template_name = 'index.html'

    def file(request):

        if request.method == 'POST':

            csvFile = request.FILES['csvfile']
            try:
                catData, quantData = FileDataService.loadData(csvFile)
                context = {
                    'categoricalData': catData,
                    'quantitativeData': quantData,
                    'filePath': "path"
                }

            except Exception as e:
                print(e)
                fil = serve(request, 'absolute_path_to_file_name')
                return render(request, 'index.html', messages.error(request, "Erro ao carregar arquivo"))
        return render(request, 'index.html', context)

    # def chart(request):
    #     if request.method == 'POST':
    #         csvFile = request.POST['file']
    #         print(csvFile)
    #
    #         context = locals()
    #         data3 = pd.DataFrame({
    #             'Eixo x': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    #             'Eixo y': [28, 55, 43, 91, 81, 53, 19, 87, 52]
    #         })
    #
    #         context['chart'] = alt.Chart(data3).mark_bar().encode(
    #             x='Eixo x',
    #             y='Eixo y'
    #         ).interactive()
    #
    #         source = data.cars()
    #         # print(data.cars());
    #         context['chart2'] = alt.Chart(source).mark_circle().encode(
    #             x='Horsepower',
    #             y='Miles_per_Gallon',
    #             color='Origin'
    #         ).interactive()
    #
    #         return None


class Chart(object):
    bar = 0
    line = 1
    scatter = 2
    pie = 3
