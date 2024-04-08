import ast
import json
from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from maintenance_manager.static.shared_staticfiles.common.utils import GeneralUtility
from maintenance_manager.static.shared_staticfiles.common.olt_api import Olt


class AttenuationUtility:
    """
    This class had methods that are used by views from attenuation_manager app
    """
    @staticmethod
    def discard_single_attenuation(db_model, register_id, attenuation_id):
        """
        Query the database and remove and register (an attenuation)
        """
        maintenance_info =  GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
        all_attenuations = maintenance_info.attenuations
        id_to_remove = attenuation_id

        for attenuation in all_attenuations:
            current_attenuation_id = attenuation.get('attenuation_id')

            if current_attenuation_id == id_to_remove:
                maintenance_info.attenuations.remove(attenuation)
                data_to_update = {"attenuations": all_attenuations}
                GeneralUtility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

                return {'error': False}

        return {'error': True}

    @staticmethod
    def save_unchanged_onts_as_first_attenuation(request, db_model):
        """
        Save records on database
        """
        try:
            body_request = json.loads(request.body)
            register_id = body_request.get('tabId')
            file_name = body_request.get('fileName')
            destination_gpon = body_request.get('destinationGpon')
            all_onts_id = body_request.get('unchangedDevices')

            data_to_update = {
                'file_name': file_name,
                'destination_gpon': destination_gpon,
                'attenuations': [{"attenuation_id": 0, "onts": all_onts_id}]
            }
             
            GeneralUtility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

            success_response = {'error': False}
            return success_response

        except Exception as err:
            error_response = {
                'error': True,
                'message': f'Ocorreu um erro ao salvar o estado inicial das atenuações. Error: {err}'
            }

            return error_response

    @staticmethod
    def get_next_attenuation(request, db_model):
        """
        Make a new query to get onts and analize to find changes on onts status
        """
        register_id = request.GET.get('tab_id')
        maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
        host = maintenance_info.source_gpon.get('host')
        pon_location = maintenance_info.source_gpon.get('gpon')
        all_attenuations = maintenance_info.attenuations
        old_onts = ast.literal_eval(maintenance_info.unchanged_onts)

        all_onts = GeneralUtility.get_onts_info_on_nmt(host, pon_location)
        onts = all_onts.get('onts')

        onts_in_current_attenuation = AttenuationUtility.separate_offline_onts_in_attenuation(old_onts, onts, all_attenuations)
        if onts_in_current_attenuation.get('error'):
            next_attenuation_info = {
                'error': True,
                'message': onts_in_current_attenuation.get('message'),
                'onts': [],
                'name': maintenance_info.file_name,
                'total_offline_onts': 0,
                'attenuations': all_attenuations,
            }
            return next_attenuation_info

        id_current_attenuation = AttenuationUtility.get_id_of_current_attenuation(all_attenuations)
        next_attenuation_info = {
            'error': False,
            'onts': onts_in_current_attenuation.get('onts'),
            'name': maintenance_info.file_name,
            'total_offline_onts': len(onts_in_current_attenuation.get('onts')),
            'attenuation_id': id_current_attenuation,
            'attenuations': all_attenuations
        }

        return next_attenuation_info

    @staticmethod
    def separate_offline_onts_in_attenuation(old_onts, onts, all_attenuations):
        """
        Obtain onts offline in the current attenuation and return it
        """
        onts_id_in_last_attenuaton = all_attenuations[len(all_attenuations)-1]['onts']
        onts_id_current_attenuation = []
        separated_off_onts = []

        for ont in onts:
            ont_status = ont.get('status')
            ont_sn = ont.get('sn')

            if ont_status == 2:
                for old_ont in old_onts:
                    old_ont_status = old_ont.get('status')
                    old_ont_sn = old_ont.get('sn')

                    if ont_sn == old_ont_sn and ont_status != old_ont_status:
                        onts_id_current_attenuation.append(ont.get('id'))
                        separated_off_onts.append(ont)

        if onts_id_current_attenuation == onts_id_in_last_attenuaton:
            return {
                'error': True,
                'message': 'As ONUs que cairam nessa atenuação são as mesmas da atenuação anterior'
            }
        
        return {'error': False, 'onts': separated_off_onts }

    @staticmethod
    def get_id_of_current_attenuation(all_attenuations):
        """
        Make a simple math operation to obtain the current attenuation ID
        """
        last_attenuation_id = all_attenuations[len(all_attenuations)-1].get('attenuation_id')
        current_attenuation_id = last_attenuation_id + 1

        return current_attenuation_id

    @staticmethod
    def save_attenuation(request, db_model, onts_in_current_attenuation, all_attenuations):
        """
        Save current attenuation in the database
        """
        register_id = request.GET.get('tab_id')
        id_of_onts = []

        for ont in onts_in_current_attenuation:
            ont_id = ont.get('id')
            id_of_onts.append(ont_id)

        current_attenuation = {
            "attenuation_id": AttenuationUtility.get_id_of_current_attenuation(all_attenuations),
            "onts": id_of_onts
        }

        all_attenuations.append(current_attenuation)

        data_to_update = {
            "attenuations": all_attenuations
        }

        GeneralUtility.update_maintenance_info_in_database(data_to_update, register_id, db_model)

    @staticmethod
    def separate_information_to_generate_commands(request, db_model):
        try:
            olt_api = Olt()
            register_id = request.GET.get('tab_id')
            onts_to_generate_commands = []
            maintenance_info = GeneralUtility.get_maintenance_info_in_database(register_id, db_model)
            unchanged_onts = ast.literal_eval(maintenance_info.unchanged_onts)
            onts_info = AttenuationUtility.get_onts_to_generate_commands(maintenance_info)
            id_devices_selected = onts_info.get('id_devices_selected')
            onts_checked = olt_api.check_vlan(unchanged_onts, maintenance_info)
            port_config = {'source_port_config': onts_checked.get('port_configuration')}

            GeneralUtility.update_maintenance_info_in_database(
                data_to_update=port_config,
                register_id=register_id,
                db_model=db_model
            )
            
            for ont in onts_checked.get('onts'):
                if int(ont['id']) in id_devices_selected:
                    onts_to_generate_commands.append(ont)

            info_to_generate_commands = {
                'register_id': register_id,
                'commands': {
                    'onts': onts_to_generate_commands,
                    'gpon': maintenance_info.destination_gpon.get('gpon'),
                    'host': maintenance_info.destination_gpon.get('host'),
                    'name': maintenance_info.file_name,
                    'old_gpon': maintenance_info.source_gpon.get('gpon'),
                    'old_host': maintenance_info.source_gpon.get('host'),
                    'destination_gpon': maintenance_info.destination_gpon,
                    'rollback': False,
                    'mode': 'attenuator'
                }, 
                'rollback': {
                    'onts': onts_to_generate_commands,
                    'gpon': maintenance_info.source_gpon['gpon'],
                    'host': maintenance_info.source_gpon['host'],
                    'name': f'{maintenance_info.file_name}-rollback',
                    'old_gpon': maintenance_info.source_gpon['gpon'],
                    'old_host': maintenance_info.source_gpon['host'],
                    'destination_gpon': maintenance_info.source_gpon,
                    'rollback': True,
                    'mode': 'attenuator'
                }
            }
            
            return info_to_generate_commands

        except ObjectDoesNotExist as err:

            message_error = {
                'error': True,
                'message': f'Ocorreu um erro ao recuperar informações no banco. Erro {err}'
            }
            return HttpResponse(json.dumps(message_error))

    @staticmethod
    def get_onts_to_generate_commands(maintenance_info):
        """
        Separates the onts in all attenuations and return it to the commands can be generated
        """
        all_attenuations = maintenance_info.attenuations
        onts_info = ast.literal_eval(maintenance_info.unchanged_onts)
        all_onts_ids_in_attenuations = []
        onts_to_generate_commands = []
        id_devices_selected = []
        

        for index in range(1, len(all_attenuations)):
            ids_onts_in_attenuation = all_attenuations[index].get('onts')

            for id_ont in ids_onts_in_attenuation:
                if id_ont not in all_onts_ids_in_attenuations:
                    all_onts_ids_in_attenuations.append(id_ont)

        for ont in onts_info:
            id_ont = ont.get('id')
            if id_ont in all_onts_ids_in_attenuations:
                id_devices_selected.append(int(id_ont))
                onts_to_generate_commands.append(ont)

        return {'onts': onts_to_generate_commands, 'id_devices_selected': id_devices_selected} 
