import asyncio
import json
import sys
import websockets
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


async def server():
    async with websockets.serve(olt, "10.0.30.252", 5678):
        await asyncio.Future()  # run forever


try:
    print('WebSocket server is running !!!')
    asyncio.run(server())
except KeyboardInterrupt:
    pass
