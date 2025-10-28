from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('render_onts_unauthorized', views.render_onts_unauthorized, name='render_onts_unauthorized'),

]