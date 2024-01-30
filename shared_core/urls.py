from django.urls import path
from . import views

urlpatterns = [
    path('render_error_page', views.render_error_page, name='render_error_page'),
]
