from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('search_onts_via_ssh', views.search_onts_via_ssh, name='search_onts_via_ssh'),
    path('update_onts_in_database', views.update_onts_in_database, name='update_onts_in_database'),
    path('get_commands', views.get_commands, name='get_commands')
]
