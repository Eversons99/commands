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
        requests.post('http://10.0.30.252:8000/generator/update_onts_in_database', headers=headers, data=body)

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

    def get_primary_description(self, gpon_info):
        """
        Connects via SSH and return gpon description "PRIMARIA XX--CABO XX"
        """
        olt_name = gpon_info.get('olt')
        pon_location = gpon_info.get("pon")
        ssh_connection = self.connect_olt(olt_name)
        output = ssh_connection.send_command_timing(f'display port desc {pon_location}')
        regex = r'\bPRIMARIA [0-9]+--[A-Z]+ [0-9]+\b' 
        desc = re.findall(regex, output)
        ssh_connection.disconnect()

        if len(desc) < 1: 
            return "PRIMÁRIA SEM DESCRIÇÃO"
        
        return desc[0]

    def update_primary_description(self, data_to_update):
        """
        Connects via SSH and update primary description
        """

        olt_name = data_to_update["gpon_info"].get('olt')
        pon_location = data_to_update["gpon_info"].get("pon")

        primary = data_to_update["desc_info"].get('primary')
        cable = data_to_update["desc_info"].get('cable')

        ssh_connection = self.connect_olt(olt_name)

        ssh_connection.send_command_timing(f'port desc {pon_location} description "PRIMARIA {primary}--CABO {cable}"')

        ssh_connection.disconnect()

        return

    def check_vlan(self, olt_name):
        pass
