import ast
import json
import requests
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .models import MaintenanceInfo


def home(request):
    """Render HTML index page"""
    return render(request, 'index.html')


def search_onts(request):
    """Receive a request and call the function to get ONTS"""
    if request.method == 'POST':
        body_request = json.loads(request.body)
        tab_id = body_request['tabId']
        source_gpon = body_request['sourceGpon']
        source_host = source_gpon['host']
        source_pon = source_gpon['gpon']

        if not tab_id or not source_gpon:
            response_message = json.dumps({
                'error': True, 
                'message': 'O host ou a localização pon não foram informados no corpo da requisição'
            })
            return HttpResponse(response_message, status=400)

        ont_devices = get_onts_via_snmp(source_host, source_pon)

        if ont_devices['error']:
            response_error = json.dumps(ont_devices)
            return HttpResponse(response_error)

        initial_maintenance_info = {
            'tab_id': tab_id,
            'file_name': None,
            'source_gpon': source_gpon,
            'destination_gpon': None,
            'unchanged_devices': ont_devices['onts'],
            'selected_devices': None,
            'commands_url': None
        }

        save_maintence_info = save_initial_maintenance_info_in_database(initial_maintenance_info)
        return HttpResponse(json.dumps(save_maintence_info))

    return redirect(home)


def get_onts_via_snmp(host, pon_location):
    """Make a request to NMT to get ONT"""
    try:
        api_url = 'https://nmt.nmultifibra.com.br/olt/onts-table'
        request_options = {
            'headers' : {'Content-Type': 'application/json; charset=utf-8'},
            'body': json.dumps({
                'gpon': pon_location,
                'host': host
            })
        }

        get_all_onts = requests.post(
            api_url, headers=request_options['headers'],
            data=request_options['body'],
            timeout=60
        )
        onts = get_all_onts.json()

        return {
            "error": False,
            "onts": onts
        }
    except requests.exceptions.RequestException as err:
        return {
            "error": True,
            "message": f'Ocorreu um erro ao buscar as ONTs no NMT. Error: {err}'
        }


def get_onts_via_ssh():
    pass


def render_error_page(request):
    """"Render error page, showing the error message"""
    error_message = {'message': request.GET.get('message')}
    return render(request, 'error.html', context=error_message)


def save_initial_maintenance_info_in_database(initial_maintenance_info):
    """Save device info in database"""
    try:
        MaintenanceInfo.objects.create(**initial_maintenance_info)
        return {
            'error': False
        }
    except IntegrityError as err:
        return {
            'error': True,
            'message': f'Erro de integridade, {err}'
        }


def render_onts_table(request):
    """Render a table with all devices (ONT's)"""
    register_id = request.GET.get('tab_id')

    if not register_id:
        error_message = {
            'message': 'O ID da guia não foi informado, impossível prosseguir'
        }

        return render(request,'error.html', context=error_message)

    try:
        device_info = get_maintenance_info_in_database(register_id)
        onts = ast.literal_eval(device_info.unchanged_devices)
        onts_context = {
            'all_devices': onts
        }
        return render(request,'ontsTable.html', context=onts_context)

    except (Exception, ObjectDoesNotExist) as err:
        error_message = {
            'error': 'True',
            'message': f'Ocorreu um erro ao buscar registro no banco. Error: {err}' 
        }

        return render(request,'error.html', context=error_message)


def get_maintenance_info_in_database(register_id):
    """Make a query in database and return an register"""
    try:
        single_register = MaintenanceInfo.objects.get(tab_id=register_id)
        return single_register

    except ObjectDoesNotExist as err:
        raise ObjectDoesNotExist from err


def get_commands(request):
    """Update maintenance info and go to NMT and get commands genereted"""
    if request.method == 'POST':
        body_request = json.loads(request.body)
        id_devices_selecteds = body_request['idDevicesSelecteds']
        destination_gpon = body_request['destinationGpon']
        file_name = body_request['fileName']
        register_id =  body_request['tabId']
        all_devices_selecteds = []

        try:
            maintenance_info = get_maintenance_info_in_database(register_id)
            unchanged_devices = ast.literal_eval(maintenance_info.unchanged_devices)

            for device in unchanged_devices:
                if int(device['id']) in id_devices_selecteds:
                    all_devices_selecteds.append(device)

        except ObjectDoesNotExist as err:
            message_error = {
                'error': True,
                'message': f'Ocorreu um erro ao recuperar/salvar informações no banco. Erro {err}' 
            }
            return HttpResponse(json.dumps(message_error))

        try:
            url = 'https://nmt.nmultifibra.com.br/olt/migration-commands'
            headers_request = {"Content-Type": "application/json; charset=utf-8"}
            options_request = json.dumps({
                'onts': all_devices_selecteds,
                'gpon': destination_gpon['gpon'],
                'host': destination_gpon['host'],
                'name': file_name,
                'oldGpon': maintenance_info.source_gpon['gpon'],
                'oldHost': maintenance_info.source_gpon['host']
            })

            commands = requests.post(url, headers=headers_request, data=options_request, timeout=60)
            commads_response = commands.json()
            data_to_update = {
                'file_name': file_name,
                'destination_gpon': destination_gpon,
                'selected_devices': all_devices_selecteds,
                'commands_url': commads_response
            }

            update_maintenance_info_in_database(data_to_update, register_id)

            return HttpResponse(json.dumps({
                "error": False, 
                'message': 'A requisição para o NMT ocorreu com sucesso'
            }))

        except (requests.exceptions.RequestException, Exception) as err:
            return HttpResponse(json.dumps({
                "error": True, 
                'message': f'Ocorreu um erro ao gerar os comandos no NMT. Error: {err}'
            }))

    return redirect(home)


def update_maintenance_info_in_database(data_to_update, register_id):
    """Update datas about maintenance info in database"""
    try:
        MaintenanceInfo.objects.filter(tab_id=register_id).update(**data_to_update)

    except Exception as err:
        raise Exception from err


def render_page_commands(request):
    """Get commands info and render commands pages"""
    register_id = request.GET.get('tab_id')
    try:
        commands = get_maintenance_info_in_database(register_id)
        commands_context = {
            'delete_commands': requests.get(commands.commands_url.get('deleteCommands')).text,
            'interface_commands': requests.get(commands.commands_url.get('interfaceCommands')).text,
            'global_commands': requests.get(commands.commands_url.get('globalCommands')).text
        }

        return render(request, 'commands.html', context=commands_context)

    except (requests.exceptions.RequestException, Exception) as err:
        error_message = {
            "message": f'Ocorreu um erro ao renderizar a página de comandos. Error: {err}'
        }

        return render(request, 'error.html', context=error_message)