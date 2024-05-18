from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('get_files', views.get_files, name='get_files')
]