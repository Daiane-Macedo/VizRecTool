import app
from django.contrib import admin
from django.urls import path

import views
from app.views import IndexView

app_name = "app"

urlpatterns = [
    path('', IndexView.as_view(), name='index_view'),
    path('chart/', IndexView.chart, name='chart')
]
