import asyncio
import json
import signal
import sys
import os
import websockets
from datetime import datetime
sys.path.append('/home/nmultifibra/commands/maintenance_manager/static/shared_staticfiles/common/')
from olt_api import Olt
from dotenv import load_dotenv
load_dotenv()


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

        elif path == '/health':
            await websocket.send(json.dumps({'status': 'OK'}))
            await websocket.close()
            

async def server():
    # Set the stop condition when receiving SIGTERM. SIGTERM is foward when the connetsion is closed
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(olt, '127.0.0.1', 8001):
        await asyncio.Future()
        await stop

try:
    asyncio.run(server())
    with open('/var/log/cmd_websocket/stdout.log', 'a', encoding='UTF-8') as log_file:
        log_file.write(f'Servidor Websocket foi inicializado com sucesso - {datetime.now()}\n')
    
    
except Exception as err:
    with open('/var/log/cmd_websocket/stderr.log', 'a', encoding='UTF-8') as log_file:
        log_file.write(f'{err}\n')

