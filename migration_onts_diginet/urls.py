from django.urls import path, include 
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('render_unauthorized_onts_table', views.render_unauthorized_onts_table, name='render_unauthorized_onts_table'),
    path('save_unauthorized_devices_on_database', views.save_unauthorized_devices_on_database, name='save_unauthorized_devices_on_database'),
]