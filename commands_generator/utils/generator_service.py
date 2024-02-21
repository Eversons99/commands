import ast
import json
from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from maintenance_manager.static.common.utils import GeneralUtility


class CommandsUtility:
    @staticmethod
    def separate_information_to_generate_commands(request, db_model):
        body_request = json.loads(request.body)
        id_devices_selected = body_request['idDevicesSelected']
        destination_gpon = body_request['destinationGpon']
        file_name = body_request['fileName']
        register_id = body_request['tabId']
        onts = []

        try:
            maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
            unchanged_onts = ast.literal_eval(maintenance_info.unchanged_onts)

            for ont in unchanged_onts:
                if int(ont['id']) in id_devices_selected:
                    onts.append(ont)

            info_to_generate_commands = {
                'onts': onts,
                'gpon': destination_gpon['gpon'],
                'host': destination_gpon['host'],
                'name': file_name,
                'old_gpon': maintenance_info.source_gpon['gpon'],
                'old_host': maintenance_info.source_gpon['host'],
                'destination_gpon': destination_gpon,
                'register_id': register_id,
                'mode': 'generator'
            }

            return info_to_generate_commands

        except ObjectDoesNotExist as err:
            message_error = {
                'error': True,
                'message': f'Ocorreu um erro ao recuperar informações no banco. Erro {err}'
            }
            return HttpResponse(json.dumps(message_error))
