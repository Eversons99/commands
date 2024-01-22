import asyncio
import datetime
import random
import websockets

async def olt(websocket, path):
    async for message in websocket:
        if path == '/get-onts':
            print(message)
            await websocket.send({''})
            #websocket.close()


async def server():
    async with websockets.serve(olt, "10.0.30.157", 5678):
        await asyncio.Future()  # run forever


try:
    print('WS is running !!!')
    asyncio.run(server())
except KeyboardInterrupt:
    pass



