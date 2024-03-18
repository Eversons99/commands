import ast
import json
import requests
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .models import SmsInfos
from dotenv import load_dotenv
load_dotenv()


def home(request):
    """Render HTML index page"""
    return render(request, 'index_sms.html')

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

        ont_devices = get_onts_snmp_in_nmt(source_host, source_pon)

        if ont_devices['error']:
            response_error = json.dumps(ont_devices)
            return HttpResponse(response_error)

        initial_sms_info = {
            'tab_id': tab_id,
            'source_gpon': source_gpon,
            'unchanged_devices': ont_devices['onts'],
            'selected_devices': None,
            'contacts': None,
            'rupture': None,
            'sms_result': None,
        }

        save_sms_info = save_sms_infos_in_database(initial_sms_info)
    
        return HttpResponse(json.dumps(save_sms_info))

    return redirect(home)

def get_onts_snmp_in_nmt(host, pon_location):
    """Make a request to NMT to get ONT"""
    try:
        api_url = 'https://nmt.nmultifibra.com.br/olt/onts-sms-table'
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
            'error': False,
            'onts': onts
        }
    except requests.exceptions.RequestException as err:
        return {
            'error': True,
            'message': f'Ocorreu um erro ao buscar as ONTs no NMT. Err: {err}'
        }

def render_error_page(request):
    """"Render error page, showing the error message"""
    error_message = {'message': request.GET.get('message')}
    return render(request, 'error.html', context=error_message)

def save_sms_infos_in_database(initial_sms_info):
    """Save device info in database"""
    try:
        SmsInfos.objects.create(**initial_sms_info)
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
        device_info = get_sms_info_in_database(register_id)
        onts = ast.literal_eval(device_info.unchanged_devices)
        onts_context = {
            'all_devices': onts
        }
        return render(request,'onts_table_sms.html', context=onts_context)

    except (Exception, ObjectDoesNotExist) as err:
        error_message = {
            'error': 'True',
            'message': f'Ocorreu um erro ao buscar registro no banco.  ' 
        }

        return render(request,'error.html', context=error_message)

def get_sms_info_in_database(register_id):
    """Make a query in database and return an register"""
    try:
        single_register = SmsInfos.objects.get(tab_id=register_id)
        return single_register

    except ObjectDoesNotExist as err:
        raise ObjectDoesNotExist from err

def update_sms_info_in_database(data_to_update, register_id):
    """Update datas about sms info in database"""
    try:
        SmsInfos.objects.filter(tab_id=register_id).update(**data_to_update)

    except Exception as err:
        raise Exception from err

def get_numbers_to_send_sms(request):
    """Update sms info and go to NMT and get numbers of clientes"""
    if request.method == 'POST':
        body_request = json.loads(request.body)
        serial_numbers_selecteds = body_request['serialNumbers']
        register_id =  body_request['tabId']

        print(serial_numbers_selecteds)

        try:
            url = 'https://nmt.nmultifibra.com.br/rompimentos/parcial'
            headers_request = {"Content-Type": "application/json; charset=utf-8"}
            options_request = json.dumps({
                'serialNumbers': serial_numbers_selecteds
            })

            contacts = requests.post(url, headers=headers_request, data=options_request, timeout=60)
            contact_response = contacts.json()

            data_to_update = {
                'contacts': {
                    'assinantes': contact_response['assinantes'],
                    'contacts': contact_response['contatos']
                }
            }

            update_sms_info_in_database(data_to_update, register_id)

            return HttpResponse(json.dumps({
                'error': False, 
                'message': 'A requisição para o NMT ocorreu com sucesso'
            }))

        except (requests.exceptions.RequestException, Exception) as err:
            return HttpResponse(json.dumps({
                'error': True, 
                'message': f'Ocorreu um erro ao coletar os contatos no NMT. Err: {err}'
            }))

    return redirect(home)

def render_contacts_page(request):
    """Get contact info and render contact pages"""
    register_id = request.GET.get('tab_id')
    try:
        sms_infos = get_sms_info_in_database(register_id)

        sms_infos = sms_infos.contacts

        contacts_context = {
            'contatos': len(sms_infos['contacts']),
            'assinantes': len(sms_infos['assinantes'])
        }

        return render(request, 'contact_page.html', context=contacts_context)

    except (requests.exceptions.RequestException, Exception) as err:
        error_message = {
            'message' :  f'ocorreu um erro ao renderizar a página de comandos. Err: {err}'
        }

        return render(request, 'error.html', context=error_message)
    
def create_rupture(request):
    """Create rupture on NMT"""
    if request.method == 'POST':
        body_request = json.loads(request.body)
        register_id =  body_request['tabId']
        previsao = body_request['previsao']
        tipo_rompimento =  body_request['tipoRompimento']

        OLTs = {
            'OLT_COTIA_01': [],
            'OLT_COTIA_02': [],
            'OLT_COTIA_03': [],
            'OLT_COTIA_04': [],
            'OLT_EMBU_01': [],
            'OLT_ITPV_01': [],
            'OLT_TRMS_01': [],
            'OLT_TRMS_02': [],
            'OLT_CCDA_01': [],
            'OLT_VGPA_01': [],
            'OLT_GRVN_01': []
        }

        sms_infos = get_sms_info_in_database(register_id)

        gpon = sms_infos.source_gpon

        OLTs[gpon['host']].append(gpon['gpon'])

        try:
            url = 'https://nmt.nmultifibra.com.br/rompimentos/pon'
            headers_request = {'Content-Type': 'application/json; charset=utf-8'}
            options_request = json.dumps({
                'previsao': previsao,
                'OLTs': OLTs,
                'tipo': tipo_rompimento
            })

            rupture = requests.post(url, headers=headers_request, data=options_request, timeout=60)
            rupture_response = rupture.json()

            data_to_update = {
                'rupture': {
                    'id': rupture_response['newRupture']['id'],
                    'previsao': rupture_response['newRupture']['previsao'],
                    'assinantes_afetados': rupture_response['newRupture']['quantidade_assinantes'],
                    'contatos': rupture_response['newRupture']['sms']['quantidade_contatos'],
                    'sms_enviado': rupture_response['newRupture']['sms']['sms_enviado'],
                    'tipo': rupture_response['newRupture']['tipo']
                }
            }

            update_sms_info_in_database(data_to_update, register_id)

            return HttpResponse(json.dumps({
                'error': False, 
                'message': 'A requisição para o NMT ocorreu com sucesso'
            }))

        except (requests.exceptions.RequestException, Exception) as err:
            return HttpResponse(json.dumps({
                'error': True, 
                'message': f'Ocorreu um erro ao criar o rompimento no NMT. Err: {err}'
            }))

def render_rupture_page(request):
    register_id = request.GET.get('tab_id')

    try:
        sms_infos = get_sms_info_in_database(register_id)

        sms_infos = sms_infos.rupture

        rupture_context = {
            'id': sms_infos['id'],
            'previsao': sms_infos['previsao'],
            'assinantes_afetados': sms_infos['assinantes_afetados'],
            'contatos': sms_infos['contatos'],
            'sms_enviado': sms_infos['sms_enviado'],
            'tipo': sms_infos['tipo']
        }


        return render(request, 'rupture_page.html', context=rupture_context)

    except (requests.exceptions.RequestException, Exception) as err:
        error_message = {
            'message' :  f'ocorreu um erro ao renderizar a página de rompimento. Err: {err}'
        }

        return render(request, 'error.html', context=error_message)
    
def send_sms(request):
    if request.method == 'POST':
        body_request = json.loads(request.body)
        register_id =  body_request['tabId']

    sms_infos = get_sms_info_in_database(register_id)
    sms_infos = sms_infos.rupture

    try:
        url = 'https://nmt.nmultifibra.com.br/rompimentos/sms'
        headers_request = {'Content-Type': 'application/json; charset=utf-8'}
        options_request = json.dumps({
            'mensagem': (
                'N-Multifibra: Identificamos um rompimento de fibra em seu bairro. '
                f'Nossa equipe ja esta no local para efetuar o reparo. Previsao de retorno: {sms_infos["previsao"]}'
                if sms_infos['tipo'].lower() == 'rompimento'
                else f'N-Multifibra: Ola, informamos que realizaremos uma manutencao de emergencia em seu bairro para melhoria da conexao. '
                f'Previsao de retorno: {sms_infos["previsao"]}'
            ),
            'index': sms_infos['id']
        })

        sms = requests.post(url, headers=headers_request, data=options_request, timeout=60)
        sms_response = sms.json()

        data_to_update = {
            'sms_result': {
                'result': sms_response
            }
        }

        update_sms_info_in_database(data_to_update, register_id)

        return HttpResponse(json.dumps({
            'error': False, 
            'message': 'A requisição para o NMT ocorreu com sucesso'
        }))

    except (requests.exceptions.RequestException, Exception) as err:
        return HttpResponse(json.dumps({
            "error": True, 
            'message': f'Ocorreu um erro ao enviar os SMS.'
        }))

def render_sms_result_page(request):
    register_id = request.GET.get('tab_id')
    try:
        sms_infos_database = get_sms_info_in_database(register_id)

        sms_result = sms_infos_database.sms_result
        rupture_infos = sms_infos_database.rupture

        rupture_context = {
            'success': sms_result['result']['success'],
            'failed': sms_result['result']['failed'],
            'previsao': rupture_infos['previsao'],
            'id': rupture_infos['id']
        }

        return render(request, 'sms_page.html', context=rupture_context)

    except (requests.exceptions.RequestException, Exception) as err:
        error_message = {
            'message' :  f'ocorreu um erro ao renderizar a página de SMS. Err: {err}'
        }

        return render(request, 'error.html', context=error_message)
