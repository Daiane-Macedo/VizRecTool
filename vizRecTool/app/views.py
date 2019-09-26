# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import render
from services.services import GraphService
from vega_datasets import data
import altair as alt
import pandas as pd


class IndexView(TemplateView):
    template_name = 'index.html'

    def chart(request):
        if request.method == 'POST':
            csvFile = request.FILES['csvfile']
            data = GraphService.buildGraph(csvFile)

        return render(request, 'index.html')

    def get(self, request, *args, **kwargs):
        context = locals()
        data3 = pd.DataFrame({
            'Eixo x': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
            'Eixo y': [28, 55, 43, 91, 81, 53, 19, 87, 52]
        })

        context['chart'] = alt.Chart(data3).mark_bar().encode(
            x='Eixo x',
            y='Eixo y'
        ).interactive()

        source = data.cars()
        # print(data.cars());
        context['chart2'] = alt.Chart(source).mark_circle().encode(
            x='Horsepower',
            y='Miles_per_Gallon',
            color='Origin'
        ).interactive()

        return render(request, self.template_name, context)


class Chart(object):
    bar = 0
    line = 1
    scatter = 2
    pie = 3
