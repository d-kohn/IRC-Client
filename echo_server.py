import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        print(f'RCVD: {message}')
        await websocket.send(f'ECHO: {message}')
        print(f'XMTD: {message}')
async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("Listening on localhost:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())