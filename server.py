import asyncio
import websockets
import os

connected_users = {}

async def handle_client(websocket, path=None):
    global connected_users
    try:
        role_message = await websocket.recv()
        
        if role_message == "ROLE:CLIENT":
            connected_users["client"] = websocket
            print("[+] Клиент подключился.")
            if "admin" in connected_users:
                await connected_users["admin"].send("[+] Клиент в сети.")
                
        elif role_message == "ROLE:ADMIN":
            connected_users["admin"] = websocket
            print("[+] Администратор подключился.")
            if "client" in connected_users:
                await websocket.send("[+] Клиент в сети.")
        else:
            await websocket.close()
            return

        async for message in websocket:
            if websocket == connected_users.get("admin"):
                if "client" in connected_users:
                    await connected_users["client"].send(message)
            elif websocket == connected_users.get("client"):
                if "admin" in connected_users:
                    await connected_users["admin"].send(message)

    except Exception:
        pass
    finally:
        if connected_users.get("client") == websocket:
            connected_users.pop("client", None)
            if "admin" in connected_users: await connected_users["admin"].send("[-] Клиент отключился.")
        if connected_users.get("admin") == websocket:
            connected_users.pop("admin", None)

port = int(os.environ.get("PORT", 10000))

async def main():
    # max_size=None отключает ограничения на размер видеокадров в облаке
    async with websockets.serve(handle_client, "0.0.0.0", port, max_size=None):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
