import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import AttenuatorDB
from maintenance_core_app.static.common.maintenance_service import MaintenanceUtility
from attenuations_manager_app.utils.attenuator_service import AttenuationUtility
from django.http.response import HttpResponse

@login_required
def home(request):
    """
    Renders the HTML index page
    """
    return render(request, 'homepageAttenuator.html')


def save_initial_attenuation_state(request):
    """
    Save the main the unchanged onts on database, this save the inital state of all devices(onts) 
    """
    if request.method == 'POST':
        db_model = AttenuatorDB
        save_main_attenuation = AttenuationUtility.save_unchanged_onts_as_first_attenuation(request, db_model)

        return HttpResponse(json.dumps(save_main_attenuation))

    return redirect(home)


def render_attenuations_page(request):
    """
    Get attenuations info on database then render it in a html template
    """
    if request.method == 'GET':
        db_model = AttenuatorDB
        register_id = request.GET.get('tab_id')
        maintenance_info = MaintenanceUtility.get_maintenance_info_in_database(register_id, db_model)

        attenuations_context = {
            'attenuations': maintenance_info.attenuations,
            'name': maintenance_info.file_name
        }

        return render(request, 'attenuationsPage.html', context=attenuations_context)

    return redirect(home)


def get_onts_to_render(request):
    """
    Query the database and return the maintenance info
    """
    if request.method == 'POST':
        body_request = json.loads(request.body)
        register_id = body_request.get('tabId')
        db_model = AttenuatorDB
        maintenance_info = MaintenanceUtility.get_maintenance_info_in_database(register_id, db_model)

        onts = {
            'attenuations': maintenance_info.attenuations,
            'unchanged_onts': maintenance_info.unchanged_onts
        }

        return HttpResponse(json.dumps(onts))

    return redirect(home)


def discard_attenuation(request):
    """
    Query the database and delete one register (that is a specific attenuation)
    """
    if request.method == 'POST':
        body_request = json.loads(request.body)
        register_id = body_request.get('tabId')
        attenuation_id = body_request.get('attenuationId')
        db_model = AttenuatorDB

        delete_attenuation = AttenuationUtility.discard_single_attenuation(db_model, register_id, attenuation_id)

        return HttpResponse(json.dumps(delete_attenuation))

    return redirect(home)


def next_attenuation(request):
    """
    Make a new query to get onts and analyze to find changes on onts status
    """
    if request.method == 'GET':
        db_model = AttenuatorDB
        next_attenuation_info = AttenuationUtility.get_next_attenuation(request, db_model)
        onts_in_current_attenuation = next_attenuation_info.get('onts')
        all_attenuations = next_attenuation_info.get('attenuations')
   
        if len(onts_in_current_attenuation) == 0:
            return render(request, 'nextAttenuationPage.html', context=next_attenuation_info)

        AttenuationUtility.save_attenuation(request, db_model, onts_in_current_attenuation, all_attenuations)
        return render(request, 'nextAttenuationPage.html', context=next_attenuation_info)

    return redirect(home)

