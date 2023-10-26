import ast
import json
import requests
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.db.utils import IntegrityError
from .models import MaintenanceInfo

# Create your views here.
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

        onts = get_onts_snmp(source_host, source_pon)

        if isinstance(onts, dict):
            response_error = ''
            if 'error' in onts.keys():
                response_error = json.dumps({
                    'error': True,
                    'message': onts['error']
                })
            else:
                response_error = json.dumps({
                    'error': True,
                    'message': f'O NMT não retornou nenhum dado apenas {onts}. Consulte novamente.'
                })
            return HttpResponse(response_error)

        maintenance_info = {
            'tab_id': tab_id,
            'file_name': None,
            'source_gpon': source_gpon,
            'destination_gpon': None,
            'unchanged_devices': onts
        }

        save_maintence_info = save_maintenance_info_in_db(maintenance_info)

        return HttpResponse(json.dumps(save_maintence_info))

    return redirect(home)

def get_onts_snmp(host, pon_location):
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
            timeout=300
        )
        onts =  get_all_onts.json()

        return onts
    except requests.exceptions.RequestException as error:
        raise requests.exceptions.RequestException(
            f'Ocorreu um erro ao buscar as ONTs no NMT{error}'
        )

def render_error_page(request):
    """"Render error page, showing the error message"""
    error_message = {'message': request.GET.get('message')}
    return render(request, 'error.html', context=error_message)

def save_maintenance_info_in_db(maintenance_info):
    """Save device info in database"""
    try:
        MaintenanceInfo.objects.create(**maintenance_info)
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
    except Exception as err:
        error_message = {
            'message': f'Ocorreu um erro ao buscar registo no banco. Error: {err}' 
        }

        return render(request,'error.html', context=error_message)

def get_maintenance_info_in_database(register_id):
    """Make a query in database and return an register"""
    try:
        single_register = MaintenanceInfo.objects.get(tab_id=register_id)
        return single_register

    except Exception:
        return Exception
