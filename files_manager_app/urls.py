from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('get_files', views.get_files, name='get_files'),
    path('show_logs', views.show_logs, name='show_logs')
]