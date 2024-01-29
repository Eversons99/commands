from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import MaintenanceInfo
from maintence_manager.static.common.utils import Utility


def home(request):
    """ Renders the HTML index page """
    return render(request, 'generatorIndex.html')


def search_onts_via_snmp(request):
    """Receives a request and call the method to get ONTS and return"""
    if request.method == 'POST':
        db_model = MaintenanceInfo
        onts_info = Utility.get_onts_via_snmp(request, db_model)
        return onts_info

    return redirect(home)


def search_onts_via_ssh(request):
    """Renders the HTML page to make a new search of ONTs via SSH"""
    db_model = MaintenanceInfo
    query_info = Utility.get_onts_via_ssh(request, db_model)
    query_info['operation_mode'] = 'generator'

    if not query_info.get('error'):
        return render(request, 'ssh_search_generator.html', context=query_info)

    return render(request, 'error.html', context=query_info)


def render_error_page(request):
    """Renders error page, showing the personalised error message"""
    error_message = {'message': request.GET.get('message')}
    return render(request, 'error.html', context=error_message)


def render_onts_table(request):
    """Render a table with all devices (ONT's)"""
    if request.method == "GET":
        try:
            db_model = MaintenanceInfo
            onts_info = Utility.get_onts_on_database(request, db_model)
            onts_info['operation_mode'] = 'generator'

            if onts_info.get('error'):
                return render(request, 'error.html', context=onts_info)

            return render(request, 'devicesTable.html', context=onts_info)

        except ObjectDoesNotExist as err:
            error_message = {
                'message': f'Ocorreu um erro ao buscar registro no banco. Error: {err}'
            }

            return render(request, 'error.html', context=error_message)


def get_commands(request):
    """Updates maintenance info and go to NMT and get commands generated"""
    if request.method == 'POST':
        db_model = MaintenanceInfo
        commands = Utility.get_commands(request, db_model)

        return commands

    return redirect(home)


def render_page_commands(request):
    """Gets commands info and render commands pages"""
    db_model = MaintenanceInfo
    commands = Utility.page_commands(request, db_model)

    if commands.get('error'):
        return render(request, 'error.html', context=commands)

    return render(request, 'commands.html', context=commands)


@csrf_exempt
def update_onts_in_database(request):
    """Updates unchanged devices on database"""
    if request.method == "POST":
        db_model = MaintenanceInfo
        Utility.update_onts_in_database(request, db_model)
