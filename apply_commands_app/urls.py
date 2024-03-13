from django.urls import path
from . import views

urlpatterns = [
    path('aplly_generated_commads', views.apply_generated_commands, name="apply_generated_commands")
]