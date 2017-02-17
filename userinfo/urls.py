#-*- coding: utf-8 -*-

import views

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^$', views.index),
    url(r'^add/', views.add),
]
