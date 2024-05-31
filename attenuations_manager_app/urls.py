from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('save_initial_attenuation_state', views.save_initial_attenuation_state, name='save_initial_attenuation_state'),
    path('render_attenuations_page', views.render_attenuations_page, name='render_attenuations_page'),
    path('get_onts_to_render', views.get_onts_to_render, name='get_onts_to_render'),
    path('discard_attenuation', views.discard_attenuation, name='discard_attenuation'),
    path('next_attenuation', views.next_attenuation, name='next_attenuation'),
    path('end_attenuations', views.end_attenuations, name='end_attenuations'),
    #path('search_onts_via_snmp', views.search_onts_via_snmp, name='search_onts_via_snmp'),
    #path('render_onts_table', views.render_onts_table, name='render_onts_table'),
    #path('render_error_page', views.render_error_page, name='render_error_page'),
    #path('render_page_commands', views.render_page_commands, name='render_page_commands'),
    #path('get_maintenance_info', views.get_maintenance_info, name='get_maintenance_info'),
    #path('save_logs', views.save_logs, name='save_logs'),
    #path('render_logs', views.render_logs, name='render_logs'),
    #path('download_command_file', views.download_command_file, name='download_command_file'),
    #path('discard_commands', views.discard_commands, name='discard_commands'),
    #path('update_status_applied_commands', views.update_status_applied_commands, name='update_status_applied_commands')
]
