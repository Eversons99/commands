import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import GeneratorDB
from django.http.response import HttpResponse
from maintenance_core_app.static.common.maintenance_service import MaintenanceUtility
from commands_generator_app.utils.generator_service import CommandsUtility


def home(request):
    """
    Renders the commands homepage
    """
    return render(request, 'homepageGenerator.html')


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

        commands = MaintenanceUtility.generate_commands(register_id, db_model, commands_info)
        rollback_commands_info['idsUsed'] = commands['response'].get('idsSelecteds')
        MaintenanceUtility.generate_commands(register_id, db_model, rollback_commands_info)

        return HttpResponse(json.dumps(commands))

    return redirect(home)


def search_onts_via_ssh(request):
    """
    Renders the HTML page to make a new search of ONTs via SSH
    """
    db_model = GeneratorDB
    query_info = MaintenanceUtility.get_gpon_info_to_query_ssh(request, db_model)

    if not query_info.get('error'):
        return render(request, 'sshSearch.html', context=query_info)

    return render(request, 'errorPage.html', context=query_info)


@csrf_exempt
def update_onts_in_database(request):
    """
    Updates unchanged devices on database
    """
    if request.method == 'POST':
        db_model = GeneratorDB
        update_status = MaintenanceUtility.update_onts_in_database(request, db_model)

        return update_status

    return redirect(home)
