from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('authenticate', views.authenticate, name='authenticate'),
    path('shared_core/search_onts_via_snmp', views.search_onts_via_snmp, name='search_onts_via_snmp'),
    path('shared_core/render_error_page', views.render_error_page, name='render_error_page'),
    path('shared_core/render_onts_table', views.render_onts_table, name='render_onts_table'),
    path('shared_core/render_page_commands', views.render_page_commands, name='render_page_commands'),
    path('shared_core/render_logs', views.render_logs, name='render_logs'),
    path('shared_core/get_maintenance_info', views.get_maintenance_info, name='get_maintenance_info'),
    path('shared_core/save_logs', views.save_logs, name='save_logs'),
    path('shared_core/download_command_file', views.download_command_file, name='download_command_files'),
    path('shared_core/discard_commands', views.discard_commands, name='discard_commands'),
    path('shared-core/check_file_names', views.check_file_names, name='check_file_names'),
    path('shared_core/update_status_applied_commands', views.update_status_applied_commands, name='update_status_applied_commands'),
    path('shared_core/generate_commands', views.generate_commands, name='generate_commands'),
    path('attenuator/', include('attenuations_manager_app.urls')),
    path('generator/', include('commands_generator_app.urls')),
    path('sms/', include('send_sms_app.urls')),
    path('files/', include('files_manager_app.urls'))
]