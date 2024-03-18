from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('attenuator/', include('attenuations_manager_app.urls')),
    path('generator/', include('commands_generator_app.urls')),
    path('sms/', include('send_sms_app.urls')),
    path('gpon/', include('gpon_health_app.urls')),
]