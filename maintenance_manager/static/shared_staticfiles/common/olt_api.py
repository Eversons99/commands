import json
import os
import re
import requests
import asyncio
from netmiko import ConnectHandler
from dotenv import load_dotenv
load_dotenv('../commands.env')

class Olt:
    def connect_olt(self, olt_name):
        """
        Connects via SSH in a OLT and return the SSH connection that will used to get info from OLT.
        """
        olt_info = requests.get(f'https://nmt.nmultifibra.com.br/olt/get-host?host={olt_name}').json()
        ip_address = olt_info[olt_name]['management']['ipv4']['primary']

        params_to_connection = {
            'device_type': 'huawei_smartax',
            'host': ip_address,
            'username': os.getenv('OLT_USER'),
            'password': os.getenv('OLT_PASS'),
            'port': 22
        }

        ssh_connection = ConnectHandler(**params_to_connection)
        ssh_connection.enable()
        ssh_connection.config_mode()

        return ssh_connection

    async def get_onts(self, websocket_connection, gpon_info):
        """
        Receives the websocket connection (websocket_connection) and some information that includes host and pon info
        (gpon_info) as an argument to connect with to an OLT and obtain information about onts. Takes information about
        the ONTs, forms a json and sends this information via the websocket connection
        """
        olt_name = gpon_info.get('host')
        pon_location = gpon_info.get("pon")
        tab_id = gpon_info.get('tab_id')
        ssh_connection = self.connect_olt(olt_name)
        all_onts = ssh_connection.send_command_timing(f'display ont in summary {pon_location}')
        collection_onts = []

        if 'There is no ONT available' in all_onts or 'Failure: The ONT does not exist' in all_onts:
            error_message = {
                "error": True,
                "message": "No ont were found"
            }
            await websocket_connection.send(json.dumps(error_message))
            ssh_connection.disconnect()
            await websocket_connection.close()

        total_number_onts = self.get_amount_of_devices_by_pon(all_onts)
        await asyncio.sleep(0.5)
        await websocket_connection.send(json.dumps(total_number_onts))

        all_onts = all_onts.splitlines()
        pattern_express = r"^  [0-9]{1,3} {0,3}\S{16} "
        for ont in all_onts:
            current_ont = {}
            if re.search(pattern_express, ont):
                ont_id = ont.split()[0]
                ont_sn = ont.split()[1]
                current_ont['id'] = ont_id
                current_ont['sn'] = ont_sn
                pon = gpon_info.get("pon").split('/')
                ont_info = ssh_connection.send_command_timing(f'display ont info {pon[0]} {pon[1]} {pon[2]} {ont_id}')
                ont_info = ont_info.splitlines()

                for info in ont_info:
                    if 'Line profile name' in info:
                        current_ont['type'] = info.split(':')[1].strip()

                    elif 'Description' in info:
                        current_ont['description'] = info.split(':')[1].strip()

                    elif 'Run state' in info:
                        status = info.split(':')[1].strip()

                        if status == 'online':
                            current_ont['status'] = 1

                        elif status == 'offline':
                            current_ont['status'] = 2

                collection_onts.append(current_ont)
                await asyncio.sleep(0.5)
                await websocket_connection.send(json.dumps(current_ont))

        headers = {"Content-Type": 'Application.json'}
        body = json.dumps({"onts": collection_onts, "tab_id": tab_id})
        requests.post('http://10.0.30.157:8000/generator/update_onts_in_database', headers=headers, data=body)

        await websocket_connection.close()
        ssh_connection.disconnect()

    def get_amount_of_devices_by_pon(self, all_onts):
        olt_output = all_onts.splitlines()
        pattern_express = re.compile(r": [0-9]{1,3},")
        amount_of_devices = {"total_number_onts": 0}

        for record in olt_output:
            record_match = pattern_express.search(record)
            if record_match:
                found_expression = record_match.group()
                amount = re.sub('[^0-9]{1,3}', '', found_expression)
                amount_of_devices['total_number_onts'] = amount

                return amount_of_devices

        return amount_of_devices

    def check_vlan(self, olt_name):
        pass
    
    def apply_commands(self, websocket, maintenance_info):
        file_name = maintenance_info.get('maintenanceInfo').get('file_name')
        commands_urls =  maintenance_info.get('maintenanceInfo').get('commands_url')
        formatted_commands = self.format_commands(commands_urls)
        
        source_info_maintenance = maintenance_info.get('maintenanceInfo').get('source_gpon')
        destination_info_maintenance = maintenance_info.get('maintenanceInfo').get('destination_gpon')
        destination_host = maintenance_info.get('maintenanceInfo').get('destination_gpon').get('host')
        
        interface_commands = formatted_commands.get('interface_commands')
        global_commands = formatted_commands.get('global_commands')
        delete_commands = formatted_commands.get('delete_commands')
        log_file = open(f'C:/Users/Everson/Desktop/commands/logs/apply_commands/{file_name}_logs.txt', 'a', encoding='utf-8')
        
        ssh_connection = self.connect_olt(destination_host)
        
        self.apply_delete_commands(
            source_info_maintenance, 
            delete_commands, 
            log_file, 
            websocket
        )
        self.apply_interface_and_global_commands(
            destination_info_maintenance, 
            ssh_connection, 
            interface_commands,
            global_commands,
            log_file, 
            websocket
        )



    def format_commands(self, commands_url):
        interface_commands = requests.get(commands_url.get('interfaceCommands')).text
        global_commands = requests.get(commands_url.get('globalCommands')).text
        delete_commands = requests.get(commands_url.get('deleteCommands')).text
        
        list_of_commands = [
            interface_commands.splitlines(),
            global_commands.splitlines(),
            delete_commands.splitlines()
        ]
        
        for commands in list_of_commands:
            for index, command in enumerate(commands):
                if command == '':
                    commands.pop(index)
        
        return { 
            "interface_commands": list_of_commands[0],
            "global_commands": list_of_commands[1],
            "delete_commands" : list_of_commands[2]
        }    

    def apply_delete_commands(self, source_info_maintenance, delete_commands, log_file, websocket):
        log_file.write('<---------------------------- DELETAR ------------------------------>\n')
        source_host = source_info_maintenance.get('host')
        ssh_connection = self.connect_olt(source_host) 
        
        for command in delete_commands:
            log_file.write(f'Applied: {command} \n\n')  
            send_command_rm = ssh_connection.send_command_timing(command)
            log_file.write(f'LOG: {send_command_rm} \n\n')
            await asyncio.sleep(0.5)
            await websocket.send(json.dumps({'command': 'command'}))

        ssh_connection.disconnect()
        
    def apply_interface_and_global_commands(destination_info_maintenance, ssh_connection, interface_commands, global_commands, log_file, websocket):
        log_file.write('<---------------------------- PROVISIONAMENTO - INTERFACE ------------------------------>\n')
        slot = destination_info_maintenance.get('gpon').split('/')[1]
        interface_command = f'interface gpon 0/{slot}'
        ssh_connection.send_command_timing(interface_command)
        
        for command_int in interface_commands:
            log_file.write(f'Applied: {command_int} \n\n')

            send_command_int = current_host.send_command_timing(command_int)

            if 'SN already exists' in send_command_int:
                delete_old_sn = self.delete_sn_duplicate(command_int, current_host)

                if delete_old_sn["success"] == False:


                elif delete_old_sn["success"] == True:
                    send_command_int = current_host.send_command_timing(command_int)


                else:
                    logging.warning(f'{file_name_selected} - O SN duplicado não pôde ser deletado')
                    log_file.write(f'LOG: *O SN duplicado não pôde ser deletado* \n\n')

            log_file.write(f'LOG: {send_command_int} \n\n')
            logs_interface.append(f'<b class="log">LOG</b>: {send_command_int}')
        
    
    def delete_sn_duplicate(command, connection_olt):
        pattern_re = re.compile('4[a-zA-Z\d]{15}') # SN
        search_sn = pattern_re.search(command)  # Search sn in command
        location = ''
        ont_id = ''

        # If find sn
        if search_sn:
            connection_olt.send_command_timing('quit')
            get_location = connection_olt.send_command_timing(f'display ont info by-sn {search_sn.group()}')
            
            for location_and_id in get_location.splitlines():
                if 'F/S/P' in location_and_id:
                    location = location_and_id.split(':')[1].strip()

                if 'ONT-ID' in location_and_id:
                    ont_id = location_and_id.split(':')[1].strip()
        
            # If find location and ont id
            if location and ont_id:
                # Do the delete commands
                try:
                    list_of_commands = format_delete_commands(location, ont_id)
    
                except Exception as err:
                    return {
                    "success": False,
                    "message": f'Erro generating delete commands - {err}'
                }   
                # applying delete commands
                delete_ont = connection_olt.send_multiline_timing(list_of_commands)
                if 'success: 1' in delete_ont:
                    return {
                        "success": True,
                        "message": 'SN was removed'
                    }
            
            return {
                "success": False,
                "message": 'Unable to get location and device id'
            }   

        return {
            "success": False,
            "message": 'The regex did not match'
        }   