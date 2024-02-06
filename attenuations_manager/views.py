import json
from django.shortcuts import render, redirect
from .models import AttenuatorDB
from maintenance_manager.static.common.utils import Utility
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse


def home(request):
    return render(request, 'attenuationsIndex.html')


def search_onts_via_snmp(request):
    """
    Call the method that get ont's info via SNMP protocol
    """
    if request.method == 'POST':
        db_model = AttenuatorDB
        onts_info = Utility.get_onts_via_snmp(request, db_model)
        return onts_info

    return redirect(home)


def render_onts_table(request):
    """
    Render a table with all onts
    """
    if request.method == "GET":
        try:
            db_model = AttenuatorDB
            onts_info = Utility.get_onts_on_database(request, db_model)

            if onts_info.get('error'):
                return render(request, 'error.html', context=onts_info)

            return render(request, 'devicesTableAtt.html', context=onts_info)

        except ObjectDoesNotExist as err:
            error_message = {
                'message': f'Ocorreu um erro ao buscar registro no banco. Error: {err}'
            }

            return render(request, 'error.html', context=error_message)


def save_initial_attenuation_state(request):
    if request.method == 'POST':
        try:
            db_model = AttenuatorDB
            body_request = json.loads(request.body)
            register_id = body_request.get('tabId')
            file_name = body_request.get('fileName')
            destination_gpon = body_request.get('fileName')
            all_onts_id = body_request.get('unchangedDevices')

            maintenance_info = {
                'file_name': file_name,
                'destination_gpon': destination_gpon,
                'attenuations': [{'attenuation_id': 0, "onts": all_onts_id}]
            }
            data_to_update = maintenance_info
            Utility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

            success_response = {'error': False}
            return HttpResponse(json.dumps(success_response))

        except Exception as err:
            error_response = {
                'error': True,
                'message': f'Ocorreu um erro ao salvar o estado inicial das atenuações. Error: {err}'
            }

            return HttpResponse(json.dumps(error_response))


def render_attenuations_page(request):
    if request.method == 'GET':
        db_model = AttenuatorDB
        register_id = request.GET.get('tab_id')
        maintenance_info = Utility.get_maintenance_info_in_database(register_id, db_model)

        attenuations_context = {
            "attenuations": maintenance_info.attenuations
        }

        return render(request, 'attenuationsPage.html', context=attenuations_context)

    return redirect('home')


def get_onts_to_render(request):
    if request.method == 'POST':
        body_request = json.loads(request.body)
        register_id = body_request.get('tabId')
        db_model = AttenuatorDB
        maintenance_info = Utility.get_maintenance_info_in_database(register_id, db_model)

        onts = {
            "attenuations": maintenance_info.attenuations,
            "unchanged_devices": maintenance_info.unchanged_devices
        }

        return HttpResponse(json.dumps(onts))




def render_error_page(request):
    """
    Renders error page, showing the personalised error message
    """
    error_message = {'message': request.GET.get('message')}
    return render(request, 'error.html', context=error_message)

