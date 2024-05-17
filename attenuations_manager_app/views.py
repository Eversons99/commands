import json
from django.shortcuts import render, redirect
from .models import AttenuatorDB
from core_app.static.shared_staticfiles.common.utils import GeneralUtility
from attenuations_manager_app.utils.attenuator_service import AttenuationUtility
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse


def home(request):
    """
    Renders the HTML index page
    """
    return render(request, 'homepageAttenuations.html')


def search_onts_via_snmp(request):
    """
    Call the method that get ont's info via SNMP protocol
    """
    if request.method == 'POST':
        db_model = AttenuatorDB
        onts_info = GeneralUtility.get_onts_via_snmp(request, db_model)
        return onts_info

    return redirect(home)


def render_onts_table(request):
    """
    Render a table with all onts
    """
    if request.method == 'GET':
        try:
            db_model = AttenuatorDB
            onts_info = GeneralUtility.get_unchanged_onts_on_database(request, db_model)

            if onts_info.get('error'):
                return render(request, 'errorPage.html', context=onts_info)

            return render(request, 'devicesTableAtt.html', context=onts_info)

        except ObjectDoesNotExist as err:
            error_message = {
                'message': f'Ocorreu um erro ao buscar registro no banco. Error: {err}'
            }

            return render(request, 'errorPage.html', context=error_message)

    return redirect(home)


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
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)

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
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)

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


def end_attenuations(request):
    """
    Gets all onts in attenuations and call the function that generate the commands
    """
    if request.method == 'GET':
        db_model = AttenuatorDB
        info_to_generate_commands = AttenuationUtility.separate_information_to_generate_commands(request, db_model)

        if info_to_generate_commands.get('error'):
            return info_to_generate_commands

        register_id = info_to_generate_commands.get('register_id')
        
        commands_info = info_to_generate_commands.get('commands')
        rollback_commands_info = info_to_generate_commands.get('rollback')
        
        commands = GeneralUtility.generate_commands(register_id, db_model, commands_info)
        rollback_commands_info['idsUsed'] = commands['response'].get('idsSelecteds')
        GeneralUtility.generate_commands(register_id, db_model, rollback_commands_info)

        return HttpResponse(json.dumps(commands))

    return redirect(home)


def render_page_commands(request):
    """
    Gets commands info and render commands pages
    """
    db_model = AttenuatorDB
    operation_mode = 'attenuator'
    commands = GeneralUtility.get_urls_to_ready_commands(request, db_model, operation_mode)
    GeneralUtility.make_file_commands(request, db_model)

    if commands.get('error'):
        return render(request, 'errorPage.html', context=commands)

    return render(request, 'attenuationsCommands.html', context=commands)


def get_maintenance_info(request):
    """
    Gets maintenance info on database and return it
    """
    if request.method == 'POST':
        db_model = AttenuatorDB
        maintenance_info = GeneralUtility.get_maintenance_info_to_apply_commands(request, db_model)

        return HttpResponse(json.dumps(maintenance_info))


def save_logs(request):
    """
    Save logs on database
    """
    if request.method == 'POST':
        db_model = AttenuatorDB
        save_logs_on_db = GeneralUtility.save_logs(request, db_model)
        
        return HttpResponse(json.dumps(save_logs_on_db))


def render_logs(request):
    """
    Gets logs on database and render a templete with all logs
    """
    if request.method == 'GET':
        register_id = json.loads(request.GET.get('tab_id'))
        rollback = json.loads(request.GET.get('rollback'))
        db_model = AttenuatorDB
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
        
        logs = {
            'logs': maintenance_info.logs, 
            'name': maintenance_info.file_name, 
            'operation_mode': 'attenuator',
        }

        if rollback:
            logs = {
                'logs': maintenance_info.rollback_logs, 
                'name': f'{maintenance_info.file_name}-rollback', 
                'operation_mode': 'attenuator',
                'rollback': True
            }

        return render(request, 'attenuatorLogs.html', context=logs)


def render_error_page(request):
    """
    Renders error page, showing the personalised error message
    """
    error_message = {'message': request.GET.get('message')}
    return render(request, 'errorPage.html', context=error_message)


def download_command_file(request):
    """
    Make an xlsx file and return it to download
    """
    if request.method == 'GET':
        db_model = AttenuatorDB
        file_commands = GeneralUtility.download_commands(request, db_model)
        return file_commands
    

def discard_commands(request):
    """
    Delete file commands
    """
    if request.method == 'DELETE':
        db_model = AttenuatorDB
        rm_commands_response = GeneralUtility.discard_commands_file(request, db_model)
        return rm_commands_response
    
def update_status_applied_commands(request):
    if request.method == 'GET':
        db_model = AttenuatorDB
        update_info = GeneralUtility.update_status_applied_commands(request, db_model)
        
        return HttpResponse(json.dumps(update_info))
