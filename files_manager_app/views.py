from commands_generator_app.models import GeneratorDB
from attenuations_manager_app.models import AttenuatorDB

from django.shortcuts import render, redirect

def home(request):
    return render(request, 'homepageFiles.html')

def get_files(request):
    if request.method == 'GET':
        selected_filter = request.GET.get('filter')
        
        map_query = {
            'Todos os comandos': None,
            'Comandos aplicados': True,
            'Comandos pendentes': False
        }
        
        query = map_query.get(selected_filter)
        if query is None:
            records_commands = GeneratorDB.objects.filter(commands_url__isnull=False)
            records_attenuator = AttenuatorDB.objects.filter(commands_url__isnull=False)
        else:
            records_commands = GeneratorDB.objects.filter(commands_applied=query, commands_url__isnull=False)
            records_attenuator = AttenuatorDB.objects.filter(commands_applied=query, commands_url__isnull=False)
        
        all_records = [
            {'record': record, 'module_name': 'Generator'} for record in records_commands
        ] + [
            {'record': record, 'module_name': 'Atenuator'} for record in records_attenuator
        ]

        context = {
            'files': all_records,
            'filtered': True,
            'selected_filter': selected_filter,
            'len_files': len(all_records)
        }
   
        return render(request, 'homepageFiles.html', context)
        
    return redirect('http://127.0.0.1:8000/files/home')