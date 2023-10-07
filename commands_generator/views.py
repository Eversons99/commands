import json
import requests
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.template import loader

# Create your views here.
def home(request):
    """Render HTML index page"""
    return render(request, 'index.html')

def search_onts(request):
    """Receive a request and call the function to get ONTS"""
    if request.method == 'POST':
        body_request = json.loads(request.body)
        source_host = body_request['sourceHost']
        source_pon_location = body_request['sourcePonLocation']

        if not source_host or not source_pon_location:
            response_message = json.dumps({
                'error': True, 
                'message': 'O host ou a localização pon não foram informados no corpo da requisição'
            })
            return HttpResponse(response_message, status=400)

        onts = get_onts_snmp(source_host, source_pon_location)

        if isinstance(onts, dict):
            response = json.dumps({
                'error': True,
                'message': onts['error']
            })
            return HttpResponse(response)
        context = {'onts': onts}
        # Salvar dados no banco
        # Retornar uma mensagem de sucesso
        return redirect(home)

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
    return redirect(request, 'error.html', context=error_message)

def render_onts_table(request):
    pass
