from maintenance_core_app.static.common.maintenance_service import MaintenanceUtility
from commands_generator_app.models import GeneratorDB
from attenuations_manager_app.models import AttenuatorDB

class FilesUtility:
    @staticmethod
    def get_files_info(request):
        selected_filter = request.GET.get('filter')
        
        map_query = {
            'Todos os comandos': None,
            'Comandos aplicados': True,
            'Comandos pendentes': False
        }

        query = map_query.get(selected_filter)
        if query is None:
            generator_files = GeneratorDB.objects.filter(commands_url__isnull=False, commands_removed=False)
            attenuator_files = AttenuatorDB.objects.filter(commands_url__isnull=False, commands_removed=False)
        else:
            generator_files = GeneratorDB.objects.filter(commands_applied=query, commands_url__isnull=False, commands_removed=False)
            attenuator_files = AttenuatorDB.objects.filter(commands_applied=query, commands_url__isnull=False, commands_removed=False)
            
        files_information = {
            'generator_files': generator_files,
            'attenuator_files': attenuator_files,
            'number_of_files': len(generator_files) + len(attenuator_files),
            'selected_filter': selected_filter
        }
        
        return files_information
    
    @staticmethod
    def format_files_to_render(files_information):
        all_db_records = [files_information.get('generator_files'), files_information.get('attenuator_files')]
        files = []

        for index, single_record in enumerate(all_db_records):

            for record  in single_record:
                module_name =  'Generator' if index == 0 else 'Attenuator'
                record_info = {
                    'record': record,
                    'module_name': module_name
                }

                if record.commands_applied:
                    record_info['apply_command_class'] = 'inactive-operation'
                    record_info['show_logs_class'] = 'active-operation'
                    record_info['disabled_apply'] = 'disabled'
                else:
                    record_info['apply_command_class'] = 'active-operation'
                    record_info['show_logs_class'] = 'inactive-operation'
                    record_info['disabled_logs'] = 'disabled'
                    
                files.append(record_info)
    
        return files
    
    @staticmethod
    def get_logs_info(request):
        last_filter_url = request.GET.get('lastFilter')
        operation_mode = request.GET.get('operationMode')
        register_id = request.GET.get('tabId')
        db_model = ''

        if operation_mode == 'generator':
            db_model = GeneratorDB
        else:
            db_model = AttenuatorDB
            
        maintenance_info = MaintenanceUtility.get_maintenance_info_in_database(register_id, db_model)

        return {
            'general_info': maintenance_info,
            'model_title': 'GC - Gerador de Comandos' if operation_mode == 'generator' else  'GA - Gerenciador de Atenuações',
            'model_name': 'generator' if operation_mode == 'generator' else 'attenuator',
            'last_filter_url': last_filter_url
        }