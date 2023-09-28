import json
import requests
from django.shortcuts import render, redirect
from django.http.response import HttpResponse

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
            error_context = {
                'error_message': f'Ocorreu um erro ao buscar as ONTS: {onts["error"]}'
            }

            return render(request, 'error.html', error_context)

        print('nada de erro')

        response = json.dumps({ 'message' :'Chegou com sucesso'})
        return HttpResponse(content=response)

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
