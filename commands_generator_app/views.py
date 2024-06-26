import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import GeneratorDB
from django.http.response import HttpResponse
from core_app.static.shared_staticfiles.common.utils import GeneralUtility
from commands_generator_app.utils.generator_service import CommandsUtility


def home(request):
    """
    Renders the HTML index page
    """
    return render(request, 'homepageGenerator.html')


def search_onts_via_snmp(request):
    """
    Call the method that get ont's info via SNMP protocol
    """
    if request.method == 'POST':
        db_model = GeneratorDB
        onts_info = GeneralUtility.get_onts_via_snmp(request, db_model)
        return onts_info

    return redirect(home)


def render_onts_table(request):
    """
    Render a table with all onts
    """
    if request.method == 'GET':
        try:
            db_model = GeneratorDB
            onts_info = GeneralUtility.get_unchanged_onts_on_database(request, db_model)
            
            if onts_info.get('error'):
                return render(request, 'errorPage.html', context=onts_info)

            return render(request, 'devicesTable.html', context=onts_info)

        except ObjectDoesNotExist as err:
            error_message = {
                'message': f'Ocorreu um erro ao buscar registro no banco. Error: {err}'
            }

            return render(request, 'errorPage.html', context=error_message)

    return redirect(home)


def get_commands(request):
    """
    Query NMT to generate commands and place the returned information in a database record
    """
    if request.method == 'POST':
        db_model = GeneratorDB
        info_to_generate_commands = CommandsUtility.separate_information_to_generate_commands(request, db_model)

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


def search_onts_via_ssh(request):
    """
    Renders the HTML page to make a new search of ONTs via SSH
    """
    db_model = GeneratorDB
    query_info = GeneralUtility.get_gpon_info_to_query_ssh(request, db_model)
    query_info['operation_mode'] = 'generator'

    if not query_info.get('error'):
        return render(request, 'ssh_search_generator.html', context=query_info)

    return render(request, 'errorPage.html', context=query_info)


def render_page_commands(request):
    """
    Gets commands info and render commands pages
    """
    db_model = GeneratorDB
    operation_mode = 'generator'
    commands = GeneralUtility.get_urls_to_ready_commands(request, db_model, operation_mode)
    GeneralUtility.make_file_commands(request, db_model)

    if commands.get('error'):
        return render(request, 'errorPage.html', context=commands)

    return render(request, 'commands.html', context=commands)


@csrf_exempt
def update_onts_in_database(request):
    """
    Updates unchanged devices on database
    """
    if request.method == 'POST':
        db_model = GeneratorDB
        update_status = GeneralUtility.update_onts_in_database(request, db_model)

        return update_status

    return redirect(home)


def get_maintenance_info(request):
    """
    Gets maintenance info on database and return it
    """
    if request.method == 'POST':
        db_model = GeneratorDB
        maintenance_info = GeneralUtility.get_maintenance_info_to_apply_commands(request, db_model)

        return HttpResponse(json.dumps(maintenance_info))


def save_logs(request):
    """
    Save logs on database
    """
    if request.method == 'POST':
        db_model = GeneratorDB
        save_logs_on_db = GeneralUtility.save_logs(request, db_model)
        
        return HttpResponse(json.dumps(save_logs_on_db))


def render_logs(request):
    """
    Gets logs on database and render a templete with all logs
    """
    if request.method == 'GET':
        register_id = json.loads(request.GET.get('tab_id'))
        rollback = json.loads(request.GET.get('rollback'))
        db_model = GeneratorDB
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)

        logs = {
            'logs': maintenance_info.logs,
            'name': maintenance_info.file_name,
            'register_id': maintenance_info.register_id,
            'operation_mode': 'generator'
        }

        if rollback:
            logs = {
                'logs': maintenance_info.rollback_logs,
                'name': f'{maintenance_info.file_name}-rollback',
                'register_id': maintenance_info.register_id,
                'operation_mode': 'generator',
                'rollback': True
            }
            
        return render(request, 'commandsLogs.html', context=logs)

        
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
        db_model = GeneratorDB
        file_commands = GeneralUtility.download_commands(request, db_model)
        return file_commands
    

def discard_commands(request):
    """
    Delete file commands
    """
    if request.method == 'DELETE':
        db_model = GeneratorDB
        commands_response = GeneralUtility.discard_commands_file(request, db_model)
        return commands_response

def update_status_applied_commands(request):
    if request.method == 'GET':
        db_model = GeneratorDB
        update_info = GeneralUtility.update_status_applied_commands(request, db_model)
        
        return HttpResponse(json.dumps(update_info))