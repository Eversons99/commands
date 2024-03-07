from django.urls import path
from . import views

urlpatterns = [
    path('query-signal', views.query_signal, name="query_signal"),
    path('get-signal-information', views.get_signal_information, name="get_signal_information"),
    path('update-desc', views.update_desc, name='update_desc'),
    path('update-primary-description', views.update_primary_description, name='update_primary_description')
]