import asyncio
import websockets
import os

async def handle_client(websocket, path=None):
    print("[+] Клиент успешно подключился к облаку через WebSockets!")
    try:
        async for message in websocket:
            print(f"[<] Получено сообщение: {message}")
            await websocket.send(f"Эхо от Render: {message}")
    except Exception as e:
        print(f"[-] Соединение разорвано: {e}")

port = int(os.environ.get("PORT", 10000))

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", port):
        print(f"[+] Облачный WebSocket-сервер стабильно запущен на порту {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
