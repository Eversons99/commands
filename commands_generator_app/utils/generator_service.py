import ast
import json
from core_app.static.shared_staticfiles.common.olt_api import Olt
from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from core_app.static.shared_staticfiles.common.utils import GeneralUtility


class CommandsUtility:
    @staticmethod
    def separate_information_to_generate_commands(request, db_model):
        body_request = json.loads(request.body)
        id_devices_selected = body_request['idDevicesSelected']
        destination_gpon = body_request['destinationGpon']
        file_name = body_request['fileName']
        register_id = body_request['tabId']
        onts = []
        olt_api = Olt()

        try:
            maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
            unchanged_onts = ast.literal_eval(maintenance_info.unchanged_onts)

            onts_checked = olt_api.check_vlan(unchanged_onts, maintenance_info)
            port_config = { 'source_port_config': onts_checked.get('port_configuration')}

            GeneralUtility.update_maintenance_info_in_database(
                data_to_update=port_config,
                register_id=register_id,
                db_model=db_model
            )

            for ont in onts_checked.get('onts'):
                if int(ont['id']) in id_devices_selected:
                    onts.append(ont)

            info_to_generate_commands = {
                'register_id': register_id,
                'commands': {
                    'onts': onts,
                    'gpon': destination_gpon['gpon'],
                    'host': destination_gpon['host'],
                    'name': f'{file_name}',
                    'old_gpon': maintenance_info.source_gpon['gpon'],
                    'old_host': maintenance_info.source_gpon['host'],
                    'destination_gpon': destination_gpon,
                    'rollback': False,
                    'mode': 'generator'
                }, 
                'rollback': {
                    'onts': onts,
                    'gpon': maintenance_info.source_gpon['gpon'],
                    'host': maintenance_info.source_gpon['host'],
                    'name': f'{file_name}-rollback',
                    'old_gpon': destination_gpon['gpon'],
                    'old_host': destination_gpon['host'],
                    'destination_gpon': maintenance_info.source_gpon,
                    'rollback': True,
                    'mode': 'generator'
                }
            }

            return info_to_generate_commands

        except ObjectDoesNotExist as err:
            message_error = {
                'error': True,
                'message': f'Ocorreu um erro ao recuperar informações no banco. Erro {err}'
            }
            return HttpResponse(json.dumps(message_error))
