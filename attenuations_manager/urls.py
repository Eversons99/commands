from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name="home"),
    path('search_onts_via_snmp', views.search_onts_via_snmp, name="search_onts_via_snmp"),
    path('render_onts_table', views.render_onts_table, name="render_onts_table"),
    path('save_initial_attenuation_state', views.save_initial_attenuation_state, name="save_initial_attenuation_state"),
    path('render_attenuations_page', views.render_attenuations_page, name="render_attenuations_page")
]
