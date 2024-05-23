from commands_generator_app.models import GeneratorDB
from attenuations_manager_app.models import AttenuatorDB
from core_app.static.shared_staticfiles.common.utils import GeneralUtility
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
            records_commands = GeneratorDB.objects.filter(commands_url__isnull=False, commands_removed=False)
            records_attenuator = AttenuatorDB.objects.filter(commands_url__isnull=False, commands_removed=False)
        else:
            records_commands = GeneratorDB.objects.filter(commands_applied=query, commands_url__isnull=False, commands_removed=False)
            records_attenuator = AttenuatorDB.objects.filter(commands_applied=query, commands_url__isnull=False, commands_removed=False)

        all_records = [
            {'record': record, 'module_name': 'Generator'} for record in records_commands
        ] + [
            {'record': record, 'module_name': 'Attenuator'} for record in records_attenuator
        ]

        context = {
            'files': all_records,
            'filtered': True,
            'selected_filter': selected_filter,
            'warn_message': 'A pesquisa não retornou nenhum arquivo' if len(all_records) == 0 else ''    
        }

        return render(request, 'homepageFiles.html', context)

    return redirect('http://127.0.0.1:8000/files/home')

def show_logs(request):
    if request.method == 'GET':
        last_filter_url = request.GET.get('lastFilter')
        operation_mode = request.GET.get('operationMode')
        register_id = request.GET.get('tabId')
        db_model = ''

        if operation_mode == 'generator':
            db_model = GeneratorDB
        else:
            db_model = AttenuatorDB
            
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
        
        context = {
            'model_title': 'GC - Gerador de Comandos' if isinstance(db_model, GeneratorDB) else  'GA - Gerenciador de Atenuações',
            'name': maintenance_info.file_name,
            'logs': maintenance_info.logs,
            'rollback_logs': maintenance_info.rollback_logs,
            'last_filter_url': last_filter_url
        }

        return render(request, 'fileLogs.html', context)
        
