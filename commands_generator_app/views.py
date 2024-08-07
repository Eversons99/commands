from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import GeneratorDB
from maintenance_core_app.static.common.maintenance_service import MaintenanceUtility
from commands_generator_app.utils.generator_service import CommandsUtility

@login_required
def home(request):
    """
    Renders the commands homepage
    """
    return render(request, 'homepageGenerator.html')


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
