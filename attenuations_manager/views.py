import ast
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
                'attenuations': [{"attenuation_id": 0, "onts": all_onts_id}]
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
            "attenuations": maintenance_info.attenuations,
            "name": maintenance_info.file_name
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


def discard_attenuation(request):
    if request.method == 'POST':
        body_request = json.loads(request.body)
        register_id = body_request.get('tabId')
        attenuation_id = body_request.get('attenuationId')
        db_model = AttenuatorDB

        delete_attenuation = Utility.discard_single_attenuation(db_model, register_id, attenuation_id)

        return HttpResponse(json.dumps(delete_attenuation))


def next_attenuation(request):
    if request.method == 'GET':
        register_id = request.GET.get('tab_id')
        db_model = AttenuatorDB
        maintenance_info = Utility.get_maintenance_info_in_database(register_id, db_model)
        host = maintenance_info.source_gpon.get('host')
        pon_location = maintenance_info.source_gpon.get('gpon')
        all_attenuations = maintenance_info.attenuations
        old_onts = ast.literal_eval(maintenance_info.unchanged_devices)

        all_onts = Utility.get_onts_info_on_nmt(host, pon_location)
        onts = all_onts.get('onts')

        onts_in_current_attenuation = separate_offline_onts_in_attenuation(old_onts, onts)
        id_current_attenuation = get_id_of_current_attenuation(all_attenuations)

        context_next_attenuation = {
            'onts': onts_in_current_attenuation,
            'name': maintenance_info.file_name,
            'total_offline_onts': len(onts_in_current_attenuation),
            'attenuation_id': id_current_attenuation,
            'attenuations': all_attenuations
        }

        if len(onts_in_current_attenuation) == 0:
            return render(request, 'nextAttenuationPage.html', context=context_next_attenuation)

        save_attenuation(register_id, onts_in_current_attenuation, all_attenuations)
        return render(request, 'nextAttenuationPage.html', context=context_next_attenuation)


def render_error_page(request):
    """
    Renders error page, showing the personalised error message
    """
    error_message = {'message': request.GET.get('message')}
    return render(request, 'error.html', context=error_message)


def separate_offline_onts_in_attenuation(old_onts, onts):
    separated_off_onts = []

    for ont in onts:
        ont_status = ont.get('status')
        ont_sn = ont.get('sn')

        if ont_status == 2:
            for old_ont in old_onts:
                old_ont_status = old_ont.get('status')
                old_ont_sn = old_ont.get('sn')

                if ont_sn == old_ont_sn and ont_status != old_ont_status:
                    separated_off_onts.append(ont)

    return separated_off_onts


def save_attenuation(register_id, onts_in_current_attenuation, all_attenuations):
    id_of_onts = []
    db_model = AttenuatorDB

    for ont in onts_in_current_attenuation:
        ont_id = ont.get('id')
        id_of_onts.append(ont_id)

    current_attenuation = {
        "attenuation_id": get_id_of_current_attenuation(all_attenuations),
        "onts": id_of_onts
    }

    all_attenuations.append(current_attenuation)

    data_to_update = {
        "attenuations": all_attenuations
    }

    Utility.update_maintenance_info_in_database(data_to_update, register_id, db_model)


def get_id_of_current_attenuation(all_attenuations):
    if len(all_attenuations) == 1:
        return 1
    else:
        return len(all_attenuations) - 1
