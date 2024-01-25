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
        olt_name = gpon_info.get('host')
        ssh_connection = self.connect_olt(olt_name)
        all_onts = ssh_connection.send_command_timing(f'display ont in summary {gpon_info.get("pon")}')
        collection_of_olts = []

        if 'There is no ONT available' in all_onts or 'Failure: The ONT does not exist' in all_onts:
            error_message = {
                "error": True,
                "message": "No ont were found"
            }
            await websocket_connection.send(json.dumps(error_message))
            ssh_connection.disconnect()
            await websocket_connection.close()

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

                await asyncio.sleep(0.5)
                await websocket_connection.send(json.dumps(current_ont))

        await websocket_connection.close()
        ssh_connection.disconnect()


    def check_vlan(self, olt_name):
        pass
