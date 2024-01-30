import ast
import json
import requests
from django.http.response import HttpResponse
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


class Utility:
    @staticmethod
    def get_onts_via_snmp(request, db_model):
        """
        Update maintenance info on database and makes a request to NMT to get onts. In NMT the ont's are searched via
        SNMP protocol. When the NMT return a response the new HttpResponse object is instantiated and returned
        """
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

        initial_maintenance_info = {
            'tab_id': tab_id,
            'source_gpon': source_gpon,
        }

        ont_devices = Utility.get_onts_info_on_nmt(source_host, source_pon)

        if ont_devices['error']:
            Utility.save_initial_maintenance_info_in_database(initial_maintenance_info, db_model)
            response_error = json.dumps(ont_devices)
            return HttpResponse(response_error)

        initial_maintenance_info['unchanged_devices'] = ont_devices['onts']
        save_maintenance_info = Utility.save_initial_maintenance_info_in_database(initial_maintenance_info, db_model)
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
        tab_id = request.GET.get('tab_id')
        if tab_id:
            maintenance_info = Utility.get_maintenance_info_in_database(tab_id, db_model)
            gpon_info = maintenance_info.source_gpon
            query_info = {
                "tab_id": tab_id,
                "pon": gpon_info.get("gpon"),
                "host": gpon_info.get("host"),
                "error": False
            }
            return query_info

        else:
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
            single_register = db_model.objects.get(tab_id=register_id)
            return single_register

        except ObjectDoesNotExist as err:
            raise ObjectDoesNotExist from err

    @staticmethod
    def get_onts_on_database(request, db_model):
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
            device_info = Utility.get_maintenance_info_in_database(register_id, db_model)
            onts = ast.literal_eval(device_info.unchanged_devices)
            onts_info = {
                'error': False,
                'all_devices': onts
            }
            return onts_info

        except ObjectDoesNotExist as err:
            raise err

    @staticmethod
    def generate_commands(request, db_model):
        """
        Gets selected devices on database and make a request to NMT to generate the commands
        """
        body_request = json.loads(request.body)
        id_devices_selected = body_request['idDevicesSelected']
        destination_gpon = body_request['destinationGpon']
        file_name = body_request['fileName']
        register_id = body_request['tabId']
        all_devices_selected = []

        try:
            maintenance_info = Utility.get_maintenance_info_in_database(register_id, db_model)
            unchanged_devices = ast.literal_eval(maintenance_info.unchanged_devices)

            for device in unchanged_devices:
                if int(device['id']) in id_devices_selected:
                    all_devices_selected.append(device)

        except ObjectDoesNotExist as err:
            message_error = {
                'error': True,
                'message': f'Ocorreu um erro ao recuperar informações no banco. Erro {err}'
            }
            return HttpResponse(json.dumps(message_error))

        try:
            url = 'https://nmt.nmultifibra.com.br/olt/migration-commands'
            headers_request = {"Content-Type": "application/json; charset=utf-8"}
            options_request = json.dumps({
                'onts': all_devices_selected,
                'gpon': destination_gpon['gpon'],
                'host': destination_gpon['host'],
                'name': file_name,
                'oldGpon': maintenance_info.source_gpon['gpon'],
                'oldHost': maintenance_info.source_gpon['host']
            })

            commands = requests.post(url, headers=headers_request, data=options_request, timeout=60)
            commands_response = commands.json()
            data_to_update = {
                'file_name': file_name,
                'destination_gpon': destination_gpon,
                'selected_devices': all_devices_selected,
                'commands_url': commands_response
            }

            Utility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

            return HttpResponse(json.dumps({
                "error": False,
                'message': 'A requisição para o NMT ocorreu com sucesso'
            }))

        except (requests.exceptions.RequestException, Exception) as err:
            return HttpResponse(json.dumps({
                "error": True,
                'message': f'Ocorreu um erro ao gerar os comandos no NMT. Error: {err}'
            }))

    @staticmethod
    def update_maintenance_info_in_database(data_to_update, register_id, db_model):
        """
         Update datas about maintenance info in database
        """
        try:
            db_model.objects.filter(tab_id=register_id).update(**data_to_update)

        except Exception as err:
            raise Exception from err

    @staticmethod
    def get_urls_to_ready_commands(request, db_model):
        """
        Make a query in the database to obtain the urls where the ready commands are stored
        """
        register_id = request.GET.get('tab_id')
        try:
            commands = Utility.get_maintenance_info_in_database(register_id, db_model)
            all_commands = {
                'error': False,
                'delete_commands': requests.get(commands.commands_url.get('deleteCommands')).text,
                'interface_commands': requests.get(commands.commands_url.get('interfaceCommands')).text,
                'global_commands': requests.get(commands.commands_url.get('globalCommands')).text
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
        register_id = request_body.get('tab_id')
        onts = request_body.get('onts')

        data_to_update = {'unchanged_devices': onts}
        Utility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

        return HttpResponse(status=200)

