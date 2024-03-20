from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('search_onts_via_snmp', views.search_onts_via_snmp, name='search_onts_via_snmp'),
    path('search_onts_via_ssh', views.search_onts_via_ssh, name='search_onts_via_ssh'),
    path('render_error_page', views.render_error_page, name='render_error_page'),
    path('render_onts_table', views.render_onts_table, name='render_onts_table'),
    path('update_onts_in_database', views.update_onts_in_database, name='update_onts_in_database'),
    path('get_commands', views.get_commands, name='get_commands'),
    path('render_page_commands', views.render_page_commands, name='render_page_commands'),
    path('get_maintenance_info', views.get_maintenance_info, name='get_maintenance_info'),
    path('save_logs', views.save_logs, name='save_logs'),
    path('render_logs', views.render_logs, name='render_logs'),
    path('download_command_file', views.download_command_file, name='download_command_files')
]
