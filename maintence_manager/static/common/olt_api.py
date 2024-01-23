import os
import requests
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
        command = ssh_connection.send_command_timing('display version')
        await websocket_connection.send(command)

        ssh_connection.disconnect()
        await websocket_connection.close()

    def check_vlan(self, olt_name):
        pass
