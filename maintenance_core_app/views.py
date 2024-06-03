import json
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .static.common.maintenance_service import MaintenanceUtility
from commands_generator_app.utils.generator_service import CommandsUtility
from attenuations_manager_app.utils.attenuator_service import AttenuationUtility
from commands_generator_app.models import GeneratorDB
from attenuations_manager_app.models import AttenuatorDB


def home(request):
    """
    Renders the 'homepage.html' template for the home page of the website.
    """
    print(request.user)
    return render(request, 'homepage.html')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html') 


def search_onts_via_snmp(request):
    """
    Call the method that get ont's info via SNMP protocol
    """
    if request.method == 'POST':
        operation_mode = json.loads(request.body).get('mode')
        db_model = GeneratorDB if operation_mode == 'generator' else AttenuatorDB
    
        onts_info = MaintenanceUtility.get_onts_via_snmp(request, db_model)
        return onts_info

    return redirect(home)


def render_error_page(request):
    """
    Renders error page, showing the personalised error message
    """
    error_info = {'message': request.GET.get('message')}
    return render(request, 'errorPage.html', context=error_info)


def render_onts_table(request):
    """
    Render a table with all onts
    """
    if request.method == 'GET':
        try:
            operation_mode = request.GET.get('mode')
            db_model = GeneratorDB if operation_mode == 'generator' else AttenuatorDB
            onts_info = MaintenanceUtility.get_unchanged_onts_on_database(request, db_model)

            onts_info['operation_mode'] = operation_mode

            if onts_info.get('error'):
                return render(request, 'errorPage.html', context=onts_info)

            return render(request, 'devicesTable.html', context=onts_info)

        except ObjectDoesNotExist as err:
            error_message = {
                'message': f'Ocorreu um erro ao buscar registro no banco. Error: {err}'
            }

            return render(request, 'errorPage.html', context=error_message)

    return redirect(home)


def render_page_commands(request):
    """
    Gets commands info and render commands pages
    """
    if request.method == 'GET':
        operation_mode = request.GET.get('mode')
        db_model = GeneratorDB if operation_mode == 'generator' else AttenuatorDB

        commands = MaintenanceUtility.get_urls_to_ready_commands(request, db_model, operation_mode)
        MaintenanceUtility.make_file_commands(request, db_model)

        if commands.get('error'):
            return render(request, 'errorPage.html', context=commands)

        return render(request, 'readyCommandsPage.html', context=commands)

    return redirect(home)


def render_logs(request):
    """
    Gets logs on database and render a templete with all logs
    """
    if request.method == 'GET':
        mode = request.GET.get('mode')
        register_id = json.loads(request.GET.get('tab_id'))
        rollback = json.loads(request.GET.get('rollback'))
        db_model = GeneratorDB if mode == 'generator' else AttenuatorDB
        maintenance_info = MaintenanceUtility.get_maintenance_info_in_database(register_id, db_model)

        logs = {
            'logs': maintenance_info.logs,
            'name': maintenance_info.file_name,
            'register_id': maintenance_info.register_id,
            'operation_mode': mode
        }

        if rollback:
            logs = {
                'logs': maintenance_info.rollback_logs,
                'name': f'{maintenance_info.file_name}-rollback',
                'register_id': maintenance_info.register_id,
                'operation_mode': mode,
                'rollback': True
            }
            
        return render(request, 'readyCommandsLogs.html', context=logs)

    return redirect(home)


def get_maintenance_info(request):
    """
    Gets maintenance info on database and return it
    """
    if request.method == 'POST':
        mode = json.loads(request.body).get('mode')
        db_model = GeneratorDB if mode == 'generator' else AttenuatorDB
        maintenance_info = MaintenanceUtility.get_maintenance_info_to_apply_commands(request, db_model)

        return HttpResponse(json.dumps(maintenance_info))

    return redirect(home)


def save_logs(request):
    """
    Save logs on database
    """
    if request.method == 'POST':
        mode = json.loads(request.body).get('mode')
        db_model = GeneratorDB if mode == 'generator' else AttenuatorDB
        save_logs_on_db = MaintenanceUtility.save_logs(request, db_model)
        
        return HttpResponse(json.dumps(save_logs_on_db))

    return redirect(home)


def download_command_file(request):
    """
    Make an xlsx file and return it to download
    """
    if request.method == 'GET':
        mode = request.GET.get('mode')
        db_model = GeneratorDB if mode == 'generator' else AttenuatorDB
        file_commands = MaintenanceUtility.download_commands(request, db_model)
        return file_commands

    return redirect(home)

def discard_commands(request):
    """
    Delete file commands
    """
    if request.method == 'DELETE':
        mode = json.loads(request.body).get('mode')
        db_model = GeneratorDB if mode == 'generator' else AttenuatorDB
        commands_response = MaintenanceUtility.discard_commands_file(request, db_model)

        return commands_response

    return redirect(home)


def check_file_names(request):
    if request.method == 'GET':
        file_names = MaintenanceUtility.check_file_names(request)

        return HttpResponse(json.dumps(file_names))

    return redirect(home)


def update_status_applied_commands(request):
    if request.method == 'GET':
        mode = request.GET.get('mode')
        db_model = GeneratorDB if mode == 'generator' else AttenuatorDB
        update_info = MaintenanceUtility.update_status_applied_commands(request, db_model)
        
        return HttpResponse(json.dumps(update_info))
    
    return redirect(home)


def generate_commands(request):
    if request.method == 'POST':
        mode = json.loads(request.body).get('mode')
        db_model = GeneratorDB if mode == 'generator' else AttenuatorDB

        if db_model == GeneratorDB:
            info_to_generate_commands = CommandsUtility.separate_information_to_generate_commands(request, db_model)
        else:
            info_to_generate_commands = AttenuationUtility.separate_information_to_generate_commands(request, db_model)

        register_id = info_to_generate_commands.get('register_id')
        
        commands_info = info_to_generate_commands.get('commands')
        rollback_commands_info = info_to_generate_commands.get('rollback')
        
        commands = MaintenanceUtility.generate_commands(register_id, db_model, commands_info)
        rollback_commands_info['idsUsed'] = commands['response'].get('idsSelecteds')
        MaintenanceUtility.generate_commands(register_id, db_model, rollback_commands_info)

        return HttpResponse(json.dumps(commands))

    return redirect(home)
