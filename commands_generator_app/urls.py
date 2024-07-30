from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('search_onts_via_ssh', views.search_onts_via_ssh, name='search_onts_via_ssh'),
    path('update_onts_in_database', views.update_onts_in_database, name='update_onts_in_database')
]
