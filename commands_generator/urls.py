from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('search_onts', views.search_onts, name='search_onts'),
    path('render_error_page', views.render_error_page, name='render_error_page'),
    path('render_onts_table', views.render_onts_table, name='render_onts_table'),
    path('get_commands', views.get_commands, name='get_commands')
]
