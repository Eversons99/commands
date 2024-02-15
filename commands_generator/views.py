from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import GeneratorDB 
from maintenance_manager.static.common.utils import GeneralUtility


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
    if request.method == "GET":
        try:
            db_model = GeneratorDB
            onts_info = GeneralUtility.get_unchanged_onts_on_database(request, db_model)

            if onts_info.get('error'):
                return render(request, 'error.html', context=onts_info)

            return render(request, 'devicesTable.html', context=onts_info)

        except ObjectDoesNotExist as err:
            error_message = {
                'message': f'Ocorreu um erro ao buscar registro no banco. Error: {err}'
            }

            return render(request, 'error.html', context=error_message)

    return redirect(home)


def get_commands(request):
    """
    Query NMT to generate commands and place the returned information in a database record
    """
    if request.method == 'POST':
        db_model = GeneratorDB
        commands = GeneralUtility.generate_commands(request, db_model)

        return commands

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

    return render(request, 'error.html', context=query_info)


def render_page_commands(request):
    """
    Gets commands info and render commands pages
    """
    db_model = GeneratorDB
    commands = GeneralUtility.get_urls_to_ready_commands(request, db_model)

    if commands.get('error'):
        return render(request, 'error.html', context=commands)

    return render(request, 'commands.html', context=commands)


@csrf_exempt
def update_onts_in_database(request):
    """
    Updates unchanged devices on database
    """
    if request.method == "POST":
        db_model = GeneratorDB
        update_status = GeneralUtility.update_onts_in_database(request, db_model)

        return update_status

    return redirect(home)


def render_error_page(request):
    """
    Renders error page, showing the personalised error message
    """
    error_message = {'message': request.GET.get('message')}
    return render(request, 'error.html', context=error_message)
