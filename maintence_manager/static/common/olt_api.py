import os
import requests
from netmiko import ConnectHandler

class Olt:
    def connect_olt(self, olt_name):
        """
        Connects via SSH in a OLT and return the SSH connection that will used to get info from OLT.
        """
        olt_info = requests.get(f'https://nmt.nmultifibra.com.br/olt/get-host?host={olt_name}').json()
        ip_address = olt_info[olt_name]['management']['ipv4']['primary']
        params_to_connection = {
            'device_type': 'huawei',
            'host': ip_address,
            'username': os.environ.get('OLT_USER'),
            'password': os.environ.get('OLT_PASS'),
            'port': 22
        }

        ssh_connection = ConnectHandler(**params_to_connection)
        ssh_connection.enable()
        ssh_connection.config_mode()

        return ssh_connection

    
    def check_vlan(self, olt_name):
        pass


    def get_onts(self, olt_name, host_info):
        ssh_connection = self.connect_olt(olt_name)