
from django.contrib import admin
from django.urls import path

from Accountapp.views import *

urlpatterns = [
    path('demo/', DemoView.as_view(), name='demo'),
]
