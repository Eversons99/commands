from django.urls import path
from . import views

urlpatterns = [
    path('query-signal', views.query_signal, name="query_signal"),
    path('get-signal-information', views.get_signal_information, name="get_signal_information")
]