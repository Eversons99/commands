import ast
from datetime import datetime, timezone
import json
import requests
import os
import pandas as pd
from attenuations_manager_app.models import AttenuatorDB
import os
import pandas as pd
from attenuations_manager_app.models import AttenuatorDB
from django.http.response import HttpResponse, FileResponse, FileResponse
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


class GeneralUtility:
    @staticmethod
    def get_onts_via_snmp(request, db_model):
        """
        Update maintenance info on database and makes a request to NMT to get onts. In NMT the ont's are searched via
        SNMP protocol. When the NMT return a response the new HttpResponse object is instantiated and returned
        """
        body_request = json.loads(request.body)
        register_id = body_request['tabId']
        source_gpon = body_request['sourceGpon']
        source_host = source_gpon['host']
        source_pon = source_gpon['gpon']

        if not register_id or not source_gpon:
            response_message = json.dumps({
                'error': True,
                'message': 'O host ou a localização pon não foram informados no corpo da requisição'
            })
            return HttpResponse(response_message, status=400)

        initial_maintenance_info = {
            "register_id": register_id,
            "source_gpon": source_gpon
        }

        ont_devices = GeneralUtility.get_onts_info_on_nmt(source_host, source_pon)

        if ont_devices['error']:
            GeneralUtility.save_initial_maintenance_info_in_database(initial_maintenance_info, db_model)
            response_error = json.dumps(ont_devices)
            return HttpResponse(response_error)

        initial_maintenance_info["unchanged_onts"] = ont_devices["onts"]
        save_maintenance_info = GeneralUtility.save_initial_maintenance_info_in_database(initial_maintenance_info, db_model)
        return HttpResponse(json.dumps(save_maintenance_info))

    @staticmethod
    def get_onts_info_on_nmt(host, pon_location):
        """
        Makes a request to NMT to get onts info, on NMT if success in the search a list with onts are returned otherwise an
        error or an empty list  is returned
        """
        try:
            api_url = 'https://nmt.nmultifibra.com.br/olt/onts-table'
            request_options = {
                'headers': {'Content-Type': 'application/json; charset=utf-8'},
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

            if not isinstance(onts, list) and onts.get('error'):
                return {
                    "error": True,
                    "onts": 0,
                    "message": onts.get('error')
                }
            
            elif len(onts) == 0 or isinstance(onts, dict):
                return {
                    "error": True,
                    "onts": 0,
                    "message": 'A busca via SNMP não retornou nenhuma informação'
                }
                

            return {
                "error": False,
                "onts": onts
            }
        except requests.exceptions.RequestException as err:
            return {
                "error": True,
                "message": f'Ocorreu um erro ao buscar as ONTs no NMT. Error: {err}'
            }

    @staticmethod
    def save_initial_maintenance_info_in_database(initial_maintenance_info, db_model):
        """
        When a new maintenance is started there is initial data that must be saved in the database, this method save
        this data on database that's received as argument
        """
        try:
            db_model.objects.create(**initial_maintenance_info)
            return {
                'error': False
            }
        except IntegrityError as err:
            return {
                'error': True,
                'message': f'Erro de integridade, {err}'
            }

    @staticmethod
    def get_gpon_info_to_query_ssh(request, db_model):
        """
        Get gpon information from the database, process this information and return a dict
        """
        register_id = request.GET.get('tab_id')
        if register_id:
            maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
            gpon_info = maintenance_info.source_gpon
            query_info = {
                "register_id": register_id,
                "pon": gpon_info.get("gpon"),
                "host": gpon_info.get("host"),
                "error": False
            }
            return query_info

        query_info = {
            "error": True,
            "message": 'Ocorreu um erro ao obter o ID da página'
        }
        return query_info

    @staticmethod
    def get_maintenance_info_in_database(register_id, db_model):
        """
        Query the database and return the desired record according to the id received as an argument
        """
        try:
            single_register = db_model.objects.get(register_id=register_id)
            return single_register

        except ObjectDoesNotExist as err:
            raise ObjectDoesNotExist from err

    @staticmethod
    def get_unchanged_onts_on_database(request, db_model):
        """
        Gets a record in the database using the id that was received as an argument (within the request). Only some
        attributes of the record are placed in a dict, this dict is returned
        """
        register_id = request.GET.get('tab_id')
        
        if not register_id:
            error_message = {
                'error': True,
                'message': 'O ID da guia não foi informado, impossível prosseguir'
            }

            return error_message

        try:
            maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
            onts = ast.literal_eval(maintenance_info.unchanged_onts)

            onts_info = {
                'error': False,
                'all_devices': onts
            }
            return onts_info

        except ObjectDoesNotExist as err:
            raise err
        
    @staticmethod
    def generate_commands(register_id, db_model, info_to_generate_commands):
        """
        Gets selected devices on database and make a request to NMT to generate the commands
        """
        try:
            url = 'https://nmt.nmultifibra.com.br/olt/migration-commands'
            headers_request = {"Content-Type": "application/json; charset=utf-8"}
            options_request = json.dumps({
                'onts': info_to_generate_commands.get('onts'),
                'gpon': info_to_generate_commands.get('gpon'),
                'host': info_to_generate_commands.get('host'),
                'name': info_to_generate_commands.get('name'),
                'oldGpon': info_to_generate_commands.get('old_gpon'),
                'oldHost': info_to_generate_commands.get('old_host'),
                'rollback': info_to_generate_commands.get('rollback'),
                'idsUsed': info_to_generate_commands.get('idsUsed')
            })

            commands = requests.post(url, headers=headers_request, data=options_request, timeout=60)
            commands_response = commands.json()

            data_to_update = {}
            
            if info_to_generate_commands.get('rollback'):
                data_to_update['rollback_commands_url'] = commands_response
            else:
                data_to_update['file_name'] = info_to_generate_commands.get('name')
                data_to_update['commands_url'] = commands_response
                data_to_update['destination_gpon'] = info_to_generate_commands.get('destination_gpon')
                data_to_update['selected_devices'] = info_to_generate_commands.get('onts')

            GeneralUtility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

            return {
                'error': False,
                'message': 'A requisição para o NMT ocorreu com sucesso',
                'response': commands_response
            }

        except (requests.exceptions.RequestException, Exception) as err:
            return {
                "error": True,
                'message': f'Ocorreu um erro ao gerar os comandos no NMT. Error: {err}'
            }

    @staticmethod
    def update_maintenance_info_in_database(data_to_update, register_id, db_model):
        """
         Update datas about maintenance info in database
        """
        try:
            db_model.objects.filter(register_id=register_id).update(**data_to_update)
        except Exception as err:
            raise Exception from err

    @staticmethod
    def get_urls_to_ready_commands(request, db_model, operation_mode):
        """
        Make a query in the database to obtain the urls where the ready commands are stored
        """
        register_id = request.GET.get('tab_id')

        try:
            commands = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)

            all_commands = {
                "error": False,
                "delete_commands": requests.get(commands.commands_url.get("deleteCommands")).text,
                "interface_commands": requests.get(commands.commands_url.get("interfaceCommands")).text,
                "global_commands": requests.get(commands.commands_url.get("globalCommands")).text,
                "maintenance_name": commands.file_name,
                "operation_mode": operation_mode
            }

            return all_commands

        except (requests.exceptions.RequestException, Exception) as err:

            error = {
                "error": True,
                "message": f'Ocorreu um erro ao renderizar a página de comandos. Error: {err}'
            }

            return error

    @staticmethod
    def update_onts_in_database(request, db_model):
        """
        Makes a request to update a record on database
        """
        request_body = json.loads(request.body)
        register_id = request_body.get("tab_id")
        onts = request_body.get("onts")

        data_to_update = {"unchanged_onts": onts}
        GeneralUtility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

        return HttpResponse(status=200)

    @staticmethod
    def get_maintenance_info_to_apply_commands(request, db_model):
        body_request = json.loads(request.body)
        register_id = body_request.get('tabId')
        maintenance = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
        maintenance_info = {
            'register_id': maintenance.register_id,
            'commands_url': maintenance.commands_url,
            'rollback_commands_url': maintenance.rollback_commands_url,
            'source_gpon': maintenance.source_gpon,
            'destination_gpon': maintenance.destination_gpon,
            'file_name': maintenance.file_name
        }
        
        return maintenance_info
    
    @staticmethod
    def save_logs(request, db_model):
        try: 
            body_request = json.loads(request.body)
            rollback = body_request.get('rollback')
            register_id = body_request.get('tabId')
            logs = body_request.get('logs')
            
            logs_to_save = {'logs': logs}

            if rollback:
                logs_to_save = {'rollback_logs': logs}

            GeneralUtility.update_maintenance_info_in_database(logs_to_save, register_id, db_model)

            return {'error': False}
        except Exception as err:
            return {'error': True, 'message': f'Ocorreu um erro ao salvar os logs. Err: {err}'}

    @staticmethod
    def make_file_commands(request, db_model):
        """
        Generates a xlsx file with ready commands and attenuation if there's
        """
        register_id = request.GET.get('tab_id')
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
        file_name = maintenance_info.file_name

        source_port_config = maintenance_info.source_port_config
        interface_commands = requests.get(maintenance_info.commands_url.get('interfaceCommands')).text
        global_commands = requests.get(maintenance_info.commands_url.get('globalCommands')).text
        delete_commands = requests.get(maintenance_info.commands_url.get('deleteCommands')).text
        interface_commands_rollback = requests.get(maintenance_info.rollback_commands_url.get('interfaceCommands')).text
        global_commands_rollback = requests.get(maintenance_info.rollback_commands_url.get('globalCommands')).text
        delete_commands_rollback = requests.get(maintenance_info.rollback_commands_url.get('deleteCommands')).text

        file = pd.ExcelWriter(f'/home/nmultifibra/commands/public/files/{file_name}.xlsx')

        df_unchanged_onts = pd.DataFrame(ast.literal_eval((maintenance_info.unchanged_onts)))     
        df_unchanged_onts['status'] = df_unchanged_onts['status'].apply(lambda x: 'online' if x == 1 else 'offline')
        df_unchanged_onts.loc[df_unchanged_onts['status'] == '1', 'status'] = 'online'
        df_unchanged_onts = df_unchanged_onts.drop(['type','description'], axis=1)
        df_unchanged_onts.to_excel(file, index=False, sheet_name="Main")

        df_source_port_config = pd.DataFrame(source_port_config.splitlines())
        df_interface_commands = pd.DataFrame(interface_commands.split('\n'))
        df_global_commands = pd.DataFrame(global_commands.split('\n'))
        df_delete_commands = pd.DataFrame(delete_commands.split('\n'))
        df_interface_commands_rollback = pd.DataFrame(interface_commands_rollback.split('\n'))
        df_global_commands_rollback = pd.DataFrame(global_commands_rollback.split('\n'))
        df_delete_commands_rollback = pd.DataFrame(delete_commands_rollback.split('\n'))
        
        if db_model == AttenuatorDB:
            attenuations = maintenance_info.attenuations
            df_attenuations = pd.DataFrame()
            
            for attenuation in attenuations[1:]:
                onts_id = attenuation.get('onts')
                onts_in_attenuation = []
                unchanged_onts = ast.literal_eval(maintenance_info.unchanged_onts)
                for ont in unchanged_onts:
                    if ont.get('id') in onts_id:
                        onts_in_attenuation.append(ont)
                
                df_attenuations = pd.DataFrame(onts_in_attenuation)
                attenuation_id = attenuation.get('attenuation_id')
                df_attenuations = df_attenuations.drop(['type', 'status', 'description'], axis=1)
                df_attenuations.to_excel(file, index=False, header=False, sheet_name=f'Atenuação {attenuation_id}')
        
        df_source_port_config.to_excel(file, index=False, header=False, sheet_name='Configs originais da porta')
        df_interface_commands.to_excel(file, index=False, header=False, sheet_name='Interface')
        df_global_commands.to_excel(file, index=False, header=False, sheet_name='Global')
        df_delete_commands.to_excel(file, index=False, header=False, sheet_name='Deletar')
        df_interface_commands_rollback.to_excel(file, index=False, header=False, sheet_name='Interface - Rollback')
        df_global_commands_rollback.to_excel(file, index=False, header=False, sheet_name='Global - Rollback')
        df_delete_commands_rollback.to_excel(file, index=False, header=False, sheet_name='Deletar - Rollback')

        file.close()

    @staticmethod
    def download_commands(request, db_model):
        """
        Reads a commands file and return your content to download
        """
        register_id = request.GET.get('tab_id')
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
        file_name = f'{maintenance_info.file_name}.xlsx'
        file_path = f'/home/nmultifibra/commands/public/files/{file_name}'

        file = open(file_path, 'rb')
        response = FileResponse(file)
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        return response
    
    @staticmethod
    def discard_commands_file(request, db_model):
        body_request = json.loads(request.body)
        register_id = body_request.get('tabId')
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
        xlsx_file = f'{maintenance_info.file_name}.xlsx'
        file_name = maintenance_info.file_name
        file_path = f'/home/nmultifibra/commands/public/files/{xlsx_file}'

        try:
            os.unlink(file_path)
            rm_file_on_nmt = requests.get(f'https://nmt.nmultifibra.com.br/files/drop-commands-file?fileName={file_name}')
            rm_file_on_nmt = rm_file_on_nmt.json()
            
            if rm_file_on_nmt.get('error'):
                raise FileNotFoundError(rm_file_on_nmt.get('error'))    
        except FileNotFoundError as err:
            error_response = {
                'error': True,
                'message': f'Erro ao deletar o arquivo {file_name}. Err: {err}'
            }
            return HttpResponse(json.dumps(error_response))
        
        data_to_update = {'commands_removed': True}
        GeneralUtility.update_maintenance_info_in_database(data_to_update, register_id, db_model) 

        success_response = {
            'error': False,
            'message': f'Arquivo {file_name} removido com sucesso'
        }
        return HttpResponse(json.dumps(success_response))

    @staticmethod
    def update_status_applied_commands(request, db_model):
        try:
            rollback = json.loads(request.GET.get('rollback'))
            register_id = json.loads(request.GET.get('tabId'))
            
            status_to_update = {
                'commands_applied': True, 
                'date_commands_applied': datetime.now(tz=timezone.utc)
            }
            
            if rollback:
                status_to_update = {
                    'rollback_commands_applied': True, 
                    'date_rollback_commands_applied': datetime.now(tz=timezone.utc)
                }
                
            GeneralUtility.update_maintenance_info_in_database(status_to_update, register_id, db_model)
            
            return {
                'error': False,
                'message': 'Status da aplicação dos comandos atualizado com sucesso'
            }

        except Exception as err:
            return {
                'error': True,
                'message': f'Ocorreu um erro ao atualizar o status da aplicação dos comandos no banco. Err: {err}'
            }