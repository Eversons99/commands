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
        
        elif path == '/health':
            await websocket.send(json.dumps({'status': 'OK'}))
            await websocket.close()
            

async def server():
    try:
        # Set the stop condition when receiving SIGTERM. SIGTERM is foward when the connetion is closed
        # loop = asyncio.get_running_loop()
        # stop = loop.create_future()
        # loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

        async with websockets.serve(olt, '127.0.0.1', 5678):
            await asyncio.Future()
            # await stop

    except Exception as err:
        print(err)
        with open(f'{os.getenv("DIR_WEBSOCKET_LOGS")}/stderr.log', 'a', encoding='UTF-8') as log_file:
            log_file.write(f'{err} - {datetime.now()}\n')


try:
    asyncio.run(server())
    with open(f'{os.getenv("DIR_WEBSOCKET_LOGS")}/stdout.log', 'a', encoding='UTF-8') as log_file:
        log_file.write(f'Servidor Websocket foi inicializado com sucesso - {datetime.now()}\n')

except Exception as err:
    with open(f'{os.getenv("DIR_WEBSOCKET_LOGS")}/stderr.log', 'a', encoding='UTF-8') as log_file:
        log_file.write(f'{err}\n')

