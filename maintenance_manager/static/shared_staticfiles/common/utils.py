import ast
import json
import requests
from django.http.response import HttpResponse
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
            "source_gpon": source_gpon,
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

            if len(onts) == 0 or isinstance(onts, dict):
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
            print(maintenance_info.unchanged_onts)
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
                'oldHost': info_to_generate_commands.get('old_host')
            })

            commands = requests.post(url, headers=headers_request, data=options_request, timeout=60)
            commands_response = commands.json()

            data_to_update = {
                'file_name': info_to_generate_commands.get('name'),
                'destination_gpon': info_to_generate_commands.get('destination_gpon'),
                'selected_devices': info_to_generate_commands.get('onts'),
                'commands_url': commands_response
            }

            GeneralUtility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

            return {
                "error": False,
                'message': 'A requisição para o NMT ocorreu com sucesso'
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
    def get_urls_to_ready_commands(request, db_model):
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
                "global_commands": requests.get(commands.commands_url.get("globalCommands")).text
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
