import json
import requests
from .utils.ixc_service import IxcApi
from .enums.olts import KnownOlts
from django.shortcuts import render, redirect


def update_desc(request):
    """
    Renderiza a página para coleta de informações
    """
    return render(request, 'updateDesc.html')

def query_signal(request):
    """
    Renderiza a página de consultar o sinal
    """
    return render(request, 'queryInfo.html')

def get_signal_information(request):
    """
    Verifica qual o modo de consulta selecionado e trata os dados de acordo com cada modo,
    no fim renderiza a tabela de as informações da consulta de sinal
    """
    if request.method == 'GET':
        query_mode = request.GET.get('queryMode')

        if query_mode == 'via_id':
            id_client = request.GET.get('queryValue')
            gpon_info = get_gpon_info_to_query_signal_via_id(id_client)

            if gpon_info.get('error'):
                error_message = {'message': gpon_info.get('message') }
                return render(request, 'error.html', context=error_message)

            if gpon_info.get('multiple_location_pon'):
                context = {'locations_pon': gpon_info.get('locations_pon')}
                return render(request, 'multipleLocation.html', context=context)

            signal_average_info = get_signal_information_by_pon_on_nmt(gpon_info)

            if signal_average_info.get('error'):
                error_message = {'message': signal_average_info.get('message') }
                return render(request, 'error.html', context=error_message)

            if signal_average_info.get('multiple_location_pon'):
                context = signal_average_info.get('locations_pon')
                return render(request, 'multipleLocation.html', context=context)
            
            return render(request, 'opticalInfo.html', context=signal_average_info)

        if query_mode == 'via_pon':
            gpon_info = json.loads(request.GET.get('queryValue'))
            signal_average_info = get_signal_information_by_pon_on_nmt(gpon_info)

            if signal_average_info.get('error'):
                error_message = {'message': signal_average_info.get('message') }
                return render(request, 'error.html', context=error_message)

            return render(request, 'opticalInfo.html', context=signal_average_info)

    return redirect(query_signal)

def get_gpon_info_to_query_signal_via_id(id_client):
    """
    Recebe o id de um cliente como argumento e faz consultas no IXC para obter sua localização PON
    """
    client_information = IxcApi.list(
        table='radusuarios',
        query_field='id_cliente',
        query_info=id_client
    )

    total_records_found = int(client_information.get('total'))

    if total_records_found == 0:
        return {
            'error': True,
            'message': 'Erro ao consultar o ID do cliente, nenhum cadastro foi localizado'
        }

    if total_records_found == 1:
        mac_client = client_information.get('registros')[0].get('onu_mac')
        client_fiber_information = IxcApi.list(
            table='radpop_radio_cliente_fibra',
            query_field='mac',
            query_info=mac_client
        )

        if client_fiber_information.get('total') == '0':
            return {
                'error': True,
                'message': f'Nenhuma ONU no campo fibra do cliente {id_client}'       
            }

        transmissor_id = client_fiber_information.get('registros')[0].get('id_transmissor')
        return {
            'error': False,
            'multiple_location_pon': False,
            'olt': KnownOlts(transmissor_id).name,
            'pon': client_fiber_information.get('registros')[0].get('ponid')
        }

    if total_records_found >= 2:
        all_pon_informations = []
        all_client_informations = client_information.get('registros')

        for client_info in all_client_informations:
            mac_client = client_info.get('onu_mac')
            fiber_information = IxcApi.list(
                table='radpop_radio_cliente_fibra',
                query_field='mac',
                query_info=mac_client
            )

            fiber_information = fiber_information.get('registros')[0]

            id_contract = client_info.get('id_contrato')
            contract_information = IxcApi.list(
                table='cliente_contrato',
                query_field='id',
                query_info=id_contract
            )

            contract_information = contract_information.get('registros')[0]
            client_default_address = contract_information.get('endereco_padrao_cliente')
            client_address = ''

            if client_default_address == 'N':
                client_address = f"{contract_information.get('endereco')} - {contract_information.get('numero')} - {contract_information.get('bairro')}"
            else:
                customer_registration = IxcApi.list(
                    table='cliente',
                    query_field='id',
                    query_info=id_client
                )
                customer_registration = customer_registration.get('registros')[0]
                client_address = f"{customer_registration.get('endereco')} - {customer_registration.get('numero')} - {customer_registration.get('bairro')}"

            transmissor_id = fiber_information['id_transmissor']

            all_pon_informations.append({
                'mac': mac_client,
                'olt': KnownOlts(transmissor_id).name,
                'pon': fiber_information['ponid'],
                'address': client_address
            })

        return {
            'error': False,
            'multiple_location_pon': True,
            'locations_pon': all_pon_informations 
        }

    return redirect(query_signal)

def get_signal_information_by_pon_on_nmt(pon):
    """
    Faz uma requisição para o NMT para obter informações sobre o sinal de uma localização pon
    """
    url = 'http://10.0.30.32:4000/monitoramento/optical-info'
    host = pon.get('olt')
    gpon = pon.get('pon')
    body_request = json.dumps({
        'host': host,
        'gpon': gpon
    })

    headers = {
        'Content-Type': 'application/json'
    }

    signal_average_info = requests.post(url, data=body_request, headers=headers)

    desc = get_primary_description(gpon, host)

    signal_average_info = signal_average_info.json()
    devices_online = signal_average_info['online']
    devices_offline = signal_average_info['offline']
    median_tx = signal_average_info['median'].get('txPower')
    median_rx = signal_average_info['median'].get('rxPower')
    signal_average_info['desc'] = desc

    if devices_online == 0 and devices_offline == 0:
        return {
            'error': True,
            'message': 'Nenhum cliente nessa localização PON'
        }

    if not median_tx or not median_rx:
        return {
            'error': True,
            'message': 'Nenhum cliente online nessa localização PON'
        }

    return signal_average_info

def update_primary_description(request):
    """
    Recebe a primária, cabo e informações GPON, após isso atualiza a descrição na OLT
    """
    if request.method == 'GET':
        olt = request.GET.get('olt')
        gpon = request.GET.get('gpon')
        primary = request.GET.get('primary')
        cable = request.GET.get('cable')

        data_to_update = {
            'gpon_info': {
                'olt': olt,
                'pon': gpon
            }, 
            'desc_info': {
                'primary': primary,
                'cable': cable
            }
        }

        data_to_update['desc_info']['old_desc'] = get_primary_description(gpon, host=olt)

        url = 'https://nmt.nmultifibra.com.br/olt/update-gpon-desc'
        body_request = json.dumps({
            'gpon': gpon,
            'host': olt,
            'value': f'PRIMARIA {primary}--CABO {cable}'
        })

        headers = {
            'Content-Type': 'application/json'
        }

        update = requests.post(url, data=body_request, headers=headers)
        update = update.json()

        if update['success']:
            return render(request, 'updated.html', context=data_to_update)
        else:
            return render(request, 'error.html')
    
def get_primary_description(gpon, host):
    """
    Faz uma requisição para o NMT para obter informações sobre a descrição da localização
    """
    url = 'https://nmt.nmultifibra.com.br/olt/get-gpon-desc'
    body_request = json.dumps({
        'gpon': gpon,
        'host': host
    })

    headers = {
        'Content-Type': 'application/json'
    }

    desc = requests.post(url, data=body_request, headers=headers)
    desc = desc.json()

    return desc['desc']
