import asyncio
import dotenv
import json
import signal
import sys
import os
import websockets
from datetime import datetime
dotenv.load_dotenv('../.env')
sys.path.append(f'{os.getenv("PROJECT_DIR")}/maintenance_core_app/static/common/')

from olt_api import Olt

async def olt(websocket, path):
    async for data in websocket:
        if path == '/get-onts':
            gpon_info = json.loads(data)
            olt = Olt()
            await olt.get_onts(websocket, gpon_info)

        elif path == '/apply-commands':
            maintenance_info = json.loads(data)
            olt = Olt()
            await olt.apply_commands(websocket, maintenance_info)

        elif path == '/get-optical-info':
            pon_info = json.loads(data)
            olt = Olt()
            await olt.get_optical_info_by_pon(websocket, pon_info)

        elif path == '/get_unauthorized_onts_by_port':
            gpon_info = json.loads(data)
            olt = Olt()
            await olt.get_unauthorized_onts_by_port(websocket, gpon_info)

        elif path == '/health':
            await websocket.send(json.dumps({'status': 'OK'}))
            await websocket.close()


async def server():
    try:
        stop = asyncio.Future()
        
        if os.name != 'nt': # nt is for Windows
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
            
        async with websockets.serve(olt, '127.0.0.1', 8001):
            print("Servidor WebSocket rodando em ws://127.0.0.1:8001")
            await stop # Wait until the stop condition is met. Signals on Linux, manual interrupt on Windows 

    except Exception as err:
        print(f'Error on websocket server: {err}')
        with open(f'{os.getenv("DIR_WEBSOCKET_LOGS")}/stderr.log', 'a', encoding='UTF-8') as log_file:
            log_file.write(f'{err} - {datetime.now()}\n')


if __name__ == '__main__':
    try:
        asyncio.run(server())
        with open(f'{os.getenv("DIR_WEBSOCKET_LOGS")}/stdout.log', 'a', encoding='UTF-8') as log_file:
            log_file.write(f'Servidor Websocket foi inicializado com sucesso - {datetime.now()}\n')

    except KeyboardInterrupt:
        print('Server interrupted manually. Shutting down...')
    except Exception as err:
        with open(f'{os.getenv("DIR_WEBSOCKET_LOGS")}/stderr.log', 'a', encoding='UTF-8') as log_file:
            log_file.write(f'{err} - {datetime.now()}\n')
