from . import views
from django.urls import path

urlpatterns = [
    path('home', views.home, name='home'),
    path('search_onts', views.search_onts, name='search_onts'),
    path('render_error_page', views.render_error_page, name='render_error_page')
]
