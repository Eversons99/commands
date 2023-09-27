from . import views
from django.urls import path

urlpatterns = [
    path('home', views.home, name='home'),
    path('search_onts', views.search_onts, name='search_onts')
]
