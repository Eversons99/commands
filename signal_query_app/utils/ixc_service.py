import json
import requests

class IxcApi:
    """
    Class que possui métodos de consulta para a API do IXC
    """
    @staticmethod
    def list(table, query_field, query_info):
        """
        Método de listar (buscar) informações em uma tabela do IXC 
        """
        url = f'https://assinante.nmultifibra.com.br/webservice/v1/{table}'
        token = "Basic MTYzOjk3NmRmZjlkNGZkNjExODdhNzUyNWQ3NGVkZmFkZGRkNTUwMzI0MGRkOTVhOTMyYjE3YjlkODRjNWU2ZGFjNTc="
        
        payload = json.dumps({
            'qtype': query_field,
            'query': query_info,
            'oper': '='
        })

        headers = {
            'ixcsoft': 'listar',
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, data=payload, headers=headers).text
        response = json.loads(response)
        return response