import json
import os
import re
import requests
import asyncio
from datetime import datetime
from netmiko import ConnectHandler
from dotenv import load_dotenv
load_dotenv(f'{os.getenv("PROJECT_DIR")}/.env')

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
        await asyncio.sleep(0.1)
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
                await asyncio.sleep(0.1)
                await websocket_connection.send(json.dumps(current_ont))

        headers = {"Content-Type": 'Application.json'}
        body = json.dumps({"onts": collection_onts, "tab_id": tab_id})
        requests.post('http://commands.nmultifibra.com.br/generator/update_onts_in_database', headers=headers, data=body)

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

    def check_vlan(self, onts, maintenance_info):
        slot = maintenance_info.source_gpon.get('gpon').split('/')[1]
        port = maintenance_info.source_gpon.get('gpon').split('/')[2]
        source_host = maintenance_info.source_gpon.get('host')
        
        ssh_connection = self.connect_olt(source_host)
        
        original_configuration = self.get_original_port_configuration(ssh_connection, maintenance_info)

        search_vlans = ssh_connection.send_command_timing(f'display service-port port 0/{slot}/{port}')
        output_olt = search_vlans.splitlines()

        exclusive_vlan = ['110', '286', '1500','1501', '1503', '1504', '1505', '1513', '1514', '1515', '1520']
        separatted_outputs_olt = [] 
        vlans_found = []
        vlans_not_found = []

        for output in output_olt:
            if 'common' in output:
                separatted_outputs_olt.append(output)

        for output in separatted_outputs_olt:

            for vlan in exclusive_vlan:

                if f'{vlan} common' in output:
                    
                    standard = re.compile(r'gpon 0/[1-9]{0,2} {0,1}/[0-9]{0,2} {0,2}[0-9]{0,3}')
                    search_id = standard.search(output)

                    if search_id:
                        get_id = search_id.group().split(' ')

                        id = get_id[len(get_id) - 1]

                        vlans_found.append({ "id": id, "vlan": vlan})

                    else:
                        vlans_not_found.append({"uutput": output, "vlan": vlan})

        for ont in onts:
            for s_vlan in vlans_found:
                if ont["id"] == s_vlan["id"]:
                    ont["vlan"] = s_vlan["vlan"]

            keys = ont.keys()
            if 'vlan' not in keys:
                ont["vlan"] = ""
        
        ssh_connection.disconnect()
        return { 'onts': onts, 'port_configuration': original_configuration} 

    async def apply_commands(self, websocket, maintenance_info):
        rollback = maintenance_info.get('maintenanceInfo').get('rollback')
        file_name = maintenance_info.get('maintenanceInfo').get('file_name')
        commands_urls = maintenance_info.get('maintenanceInfo').get('commands_url')
        source_info_maintenance = maintenance_info.get('maintenanceInfo').get('source_gpon')
        destination_info_maintenance = maintenance_info.get('maintenanceInfo').get('destination_gpon')
        destination_host = maintenance_info.get('maintenanceInfo').get('destination_gpon').get('host')
        
        if rollback:
            file_name = f'{file_name}-rollback'
            commands_urls = maintenance_info.get('maintenanceInfo').get('rollback_commands_url')
            source_info_maintenance = maintenance_info.get('maintenanceInfo').get('destination_gpon')
            destination_info_maintenance = maintenance_info.get('maintenanceInfo').get('source_gpon')
            destination_host = maintenance_info.get('maintenanceInfo').get('source_gpon').get('host')

        formatted_commands = self.format_commands(commands_urls)
        interface_commands = formatted_commands.get('interface_commands')
        global_commands = formatted_commands.get('global_commands')
        delete_commands = formatted_commands.get('delete_commands')
        log_file = open(f'{os.getenv("PROJECT_DIR")}/logs/apply_commands/{file_name}_logs.txt', 'a', encoding='utf-8')
        
        ssh_connection = self.connect_olt(destination_host)
        
        await self.apply_delete_commands(source_info_maintenance, delete_commands, log_file, websocket)
        await self.apply_interface_and_global_commands(destination_info_maintenance, ssh_connection, interface_commands, global_commands, log_file, websocket)

        ssh_connection.disconnect()
        log_file.close()
        await websocket.close()

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

    async def apply_delete_commands(self, source_info_maintenance, delete_commands, log_file, websocket):
        log_file.write('<---------------------------- DELETAR ------------------------------>\n')
        source_host = source_info_maintenance.get('host')
        ssh_connection = self.connect_olt(source_host) 
        
        for command in delete_commands:
            log_file.write(f'APPLIED: {command} \n\n')  
            send_command_rm = ssh_connection.send_command_timing(command)
            log_file.write(f'LOG: {send_command_rm} \n\n')
            await asyncio.sleep(0.1)
            await websocket.send(json.dumps({'command': f'{command}', 'log': send_command_rm}))

        ssh_connection.disconnect()
        
    async def apply_interface_and_global_commands(self, destination_info_maintenance, ssh_connection, interface_commands, global_commands, log_file, websocket):
        log_file.write('<---------------------------- PROVISIONAMENTO - INTERFACE ------------------------------>\n')
        slot = destination_info_maintenance.get('gpon').split('/')[1]
        interface_command = f'interface gpon 0/{slot}'
        ssh_connection.send_command_timing(interface_command)
        
        for command in interface_commands:
            log_file.write(f'APPLIED: {command} \n\n')
            send_command_int = ssh_connection.send_command_timing(command)

            if 'SN already exists' in send_command_int:
                log_file.write(f'ERROR: SN DUPLICADO LOCALIZADO EM {command}')
                delete_old_sn = self.delete_sn_duplicate(command, ssh_connection)

                if not delete_old_sn["success"]:
                    ssh_connection.send_command_timing(interface_command)
                    log_file.write(f'ERROR: Erro ao deletear ONU duplicada: {delete_old_sn["message"]}')

                elif delete_old_sn["success"]:
                    ssh_connection.send_command_timing(interface_command)
                    send_command_int = ssh_connection.send_command_timing(command)
                    log_file.write('INFO: O SN duplicado foi deletado e o comando foi aplicado novamente')

            log_file.write(f'LOG: {send_command_int} \n\n')
            await asyncio.sleep(0.1)
            await websocket.send(json.dumps({'command': f'{command}', 'log': send_command_int}))
        
        log_file.write('<---------------------------- PROVISIONAMENTO - GLOBAL ------------------------------>\n')
        ssh_connection.send_command_timing('quit')
        
        for command in global_commands:
            log_file.write(f'APPLIED: {command} \n\n')
            send_command_gbl = ssh_connection.send_command_timing(command)
            log_file.write(f'LOG: {send_command_gbl} \n\n')
            await asyncio.sleep(0.1)
            await websocket.send(json.dumps({'command': f'{command}', 'log': send_command_gbl}))

    def delete_sn_duplicate(self, command, ssh_connection):
        pattern_re = re.compile('4[a-zA-Z\d]{15}') # SN
        search_sn = pattern_re.search(command)  # Search sn in command
        location = ''
        ont_id = ''

        # If find sn
        if search_sn:
            ssh_connection.send_command_timing('quit')
            get_location = ssh_connection.send_command_timing(f'display ont info by-sn {search_sn.group()}')
            
            for location_and_id in get_location.splitlines():
                if 'F/S/P' in location_and_id:
                    location = location_and_id.split(':')[1].strip()

                if 'ONT-ID' in location_and_id:
                    ont_id = location_and_id.split(':')[1].strip()

            if location and ont_id:
                list_of_commands = self.format_delete_commands(location, ont_id)
                delete_ont = ssh_connection.send_multiline_timing(list_of_commands)

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
        
    def format_delete_commands(self, location, ont_id):
        location_splited = location.split('/')
        slot = location_splited[1]
        port = location_splited[2]

        list_of_delete_commands = [
            f'undo service-port port 0/{slot}/{port} ont {ont_id}',
            'y',
            f'interface gpon 0/{slot}',
            f'ont delete {port} {ont_id}',
        ]

        return list_of_delete_commands

    def get_original_port_configuration(self, ssh_connection, maintenance_info):
        location_pon = maintenance_info.source_gpon.get('gpon')
        configuration = ssh_connection.send_command_timing(f'display current-configuration port {location_pon}')
        
        return configuration
    
    async def get_optical_info(self, websocket, olt_name, pon):
        ssh_connection = self.connect_olt(olt_name)
        reg_pattern = r'^[0-9]\/([0-1]?[0-9]|20)\/([0-1]?[0-9]|20)$'

        if not re.match(reg_pattern, pon):            
            message = {
                'status' : 'failed', 
                'message': 'Localização pon fora do padrão. Exemplo (0/1/1)'
            }
            ssh_connection.disconnect()
            await asyncio.sleep(0.1)
            await websocket.send(json.dumps(message))
            await websocket.close()

        directives = pon.split('/')
        pon_slot = directives[1]
        pon_port = directives[2]

        signal_info = ssh_connection.send_multiline_timing([
            f'interface gpon 0/{pon_slot}',
            f'display ont info {pon_port} all',
            f'display ont optical-info {pon_port} all'
        ])

        signal_info = signal_info.splitlines()
        signal_on_port = []
        amount_onts = {}
        start_position = 0
        
        for index, info in enumerate(signal_info):
            if 'ONTs are' in info:
                if len(info.split()) == 13:
                    amount_onts['online'] = int(info.split()[-1])
                    amount_onts['offline'] = int(info.split()[10].split(',')[0]) - amount_onts['online']
                    amount_onts['total'] = int(info.split()[10].split(',')[0])
                else:
                    amount_onts['online'] = int(info.split()[-1])
                    amount_onts['offline'] = int(info.split()[9].split(',')[0]) - amount_onts['online']
                    amount_onts['total'] = int(info.split()[9].split(',')[0])
    
            if '(dBm)' in info:
                start_position = index + 2
                break

        for index, info in enumerate(signal_info[start_position:]):
            if len(info.split()) == 8:
                signal_on_port.append({
                    'rx_power': info.split()[1],
                    'tx_power': info.split()[3],
                })

        ssh_connection.disconnect()
        optical_port_info = {'signal_on_port':signal_on_port, 'amount_onts': amount_onts}
        return optical_port_info
    
    async def format_optical_info(self, optical_info):
        all_tx_power = 0
        all_rx_power = 0

        if optical_info.get('amount_onts').get('online') == 0:
            return {
                'online': optical_info.get('amount_onts').get('online'),
                'offline': optical_info.get('amount_onts').get('offline'),
                'median': { 'rxPower': None, 'txPower':None },
                'best': { 'rxPower': None, 'txPower': None },
                'worst': { 'rxPower': None, 'txPower': None }
            }
            
        formatted_optical = {
            'online': int(optical_info.get('amount_onts').get('online')),
            'offline': int(optical_info.get('amount_onts').get('offline')),
            'median': {},
            'best': {},
            'worst': {}
        }

        for index, signal in enumerate(optical_info.get('signal_on_port')):
            rx_power = float(signal.get('rx_power'))
            tx_power = float(signal.get('tx_power'))
            if index == 0 :
                formatted_optical['best']['rxPower'] = rx_power
                formatted_optical['best']['txPower'] = tx_power
                formatted_optical['worst']['rxPower'] = rx_power
                formatted_optical['worst']['txPower'] = tx_power

            if index > 0:
                if rx_power < formatted_optical['worst']['rxPower']:
                    formatted_optical['worst']['rxPower'] = rx_power

                if tx_power < formatted_optical['worst']['txPower']:
                    formatted_optical['worst']['txPower'] = tx_power

                if rx_power > formatted_optical['best']['rxPower']:
                    formatted_optical['best']['rxPower'] = rx_power

                if tx_power > formatted_optical['best']['txPower']:
                    formatted_optical['best']['txPower'] = tx_power

            all_rx_power = all_rx_power + float(rx_power)
            all_tx_power = all_tx_power + float(tx_power)

        formatted_optical['median']['rxPower'] = round(all_rx_power / optical_info.get('amount_onts').get('online'), 2)
        formatted_optical['median']['txPower'] = round(all_tx_power / optical_info.get('amount_onts').get('online'), 2)

        return formatted_optical
    
    async def get_optical_info_by_pon(self, websocket, pon_info):
        try:
            with open(f'{os.getenv("DIR_WEBSOCKET_LOGS")}/stdout.log', 'a', encoding='UTF-8') as log_file:
                log_file.write(f'GET OPTICAL INFO: {pon_info} - {datetime.now()}\n')
                    
            pon = pon_info.get('pon')
            olt_name = pon_info.get('olt')
            optical_info = await self.get_optical_info(websocket, olt_name, pon)
        
            if isinstance(optical_info, dict) and optical_info.get('status') == 'failed':
                await asyncio.sleep(0.1)
                await websocket.send(json.dumps(optical_info))
                await websocket.close()
                
            formatted_optical_info = await self.format_optical_info(optical_info)
            await asyncio.sleep(0.1) 
            await websocket.send(json.dumps({'status': 'success', 'opticalInfo': formatted_optical_info}))

        except Exception as err:
            message = {
                'status': 'failed',
                'message': f'Ocorreu um erro ao buscar informaçõe de sinal. Err: {err}'
            }
            await asyncio.sleep(0.1)
            await websocket.send(json.dumps(message))
            await websocket.close()
        