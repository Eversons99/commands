"""maintenance_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("attenuator/", include("attenuations_manager_app.urls")),
    path("generator/", include("commands_generator_app.urls")),
    path("sms/", include("send_sms_app.urls")),
    path("gpon/", include("gpon_health_app.urls")),
    path("apply/", include("apply_commands_app.urls")),
    path("admin/", admin.site.urls),
]
