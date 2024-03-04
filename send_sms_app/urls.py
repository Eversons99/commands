from django.urls import path
from . import views


urlpatterns = [
    path('home', views.home, name='home'),
    path('search_onts', views.search_onts, name='search_onts'),
    path('render_error_page', views.render_error_page, name='render_error_page'),
    path('render_onts_table', views.render_onts_table, name='render_onts_table'),
    path('get_contacts', views.get_numbers_to_send_sms, name='get_contacts'),
    path('render_contacts_page', views.render_contacts_page, name='render_contacts_page'),
    path('create_rupture', views.create_rupture, name='create_rupture'),
    path('render_rupture_page', views.render_rupture_page, name='render_rupture_page'),
    path('send_sms', views.send_sms, name='send_sms'),
    path('render_sms_result_page', views.render_sms_result_page, name='render_sms_result_page'),
]