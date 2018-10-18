from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('data_source', view.data_source, name='data_source'),
]
