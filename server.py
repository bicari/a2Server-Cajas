import socketio
import asyncio
import pathlib
import uvicorn.server
import uvicorn.config
import os
from read_ini import getKeys
server_sio = socketio.AsyncServer(async_mode='asgi',  logger=True, always_connect=False, cors_allowed_origins = '*', Engineio_logger=True, ping_timeout=60, ping_interval=30)
app = socketio.ASGIApp(server_sio)
connected_clients = set()

class NamespaceServer(socketio.AsyncNamespace):
    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.namespace = namespace #Espacio de nombre donde el cliente se conectara el cual sera unico para cada caja conectada


    async def on_start_task(self, sid, data):
         print(data)

    async def on_get_data_cajas(self, data: dict):
         pass

    async def on_connect(self, sid, environ):
        self.headers_client_serie = environ['asgi.scope']['headers'][1][1].decode('utf-8')
        connected_clients.add(self.headers_client_serie)
        print(connected_clients)

    async def on_disconnect(self, sid):
         connected_clients.discard(self.headers_client_serie)
         print(connected_clients)    

for serie in getKeys():#Obteniendo series disponibles de las cajas, y creando instancias de namespaces
    if serie != None:
        server_sio.register_namespace(NamespaceServer(f"/{serie.upper()}"))


if __name__ == '__main__':
    if not os.path.exists(f"{pathlib.Path().absolute()}\\tmp"):
            os.mkdir(f"{pathlib.Path().absolute()}\\tmp")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
            os.mkdir(f"{pathlib.Path().absolute()}\\zip")        

    uvicorn.run(app, host='127.0.0.1', port=8000)

