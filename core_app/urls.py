from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shared-core/check_file_names', views.check_file_names, name='check_file_names'),
    path('attenuator/', include('attenuations_manager_app.urls')),
    path('generator/', include('commands_generator_app.urls')),
    path('sms/', include('send_sms_app.urls')),
    path('gpon/', include('gpon_health_app.urls')),
    path('files/', include('files_manager_app.urls'))
]