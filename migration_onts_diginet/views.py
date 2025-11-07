import json
from django.http import HttpResponse
from django.shortcuts import render
from .models import DiginetOntsMigrationDB

# Create your views here.
def home(request):
    return render(request, 'migrationDiginetHome.html')

def save_unauthorized_devices_on_database(request):
    if request.method == 'POST':
        try:
            print({
                'register_id': json.loads(request.body).get('tabId'),
                'pon': json.loads(request.body).get('pon'),
                'host': json.loads(request.body).get('host'),
                'serial_numbers': json.loads(request.body).get('serialNumbers'),
            })
            DiginetOntsMigrationDB.objects.create(
                register_id = json.loads(request.body).get('tabId'),
                pon = json.loads(request.body).get('pon'),
                host = json.loads(request.body).get('host'),
                serial_numbers = json.loads(request.body).get('serialNumbers')
            )

            return HttpResponse(status=200)
        except Exception as err:
            return HttpResponse(
                status = 500, 
                content = f'Erro ao salvar dispositivos não autorizado no banco: {err}'
            )

        
def render_unauthorized_onts_table():
    pass