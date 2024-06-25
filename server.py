import socketio
import asyncio
import pathlib
import uvicorn.server
import uvicorn.config
import os
import base64
from read_ini import getKeys

from functions.search_tables import search_database_files

server_sio = socketio.AsyncServer(async_mode='asgi',  logger=True, always_connect=False, cors_allowed_origins = '*', Engineio_logger=True, ping_timeout=60, ping_interval=30)
app = socketio.ASGIApp(server_sio)
connected_clients = list()

class NamespaceServer(socketio.AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace)
        self.namespace = namespace #Espacio de nombre donde el cliente se conectara el cual sera unico para cada caja conectada


    async def start_task(self):
        max_size_file = 1024*1024
        iter = 0
        if await search_database_files() == True:
            size_file = os.path.getsize('data.zip')
            with open('data.zip', 'rb') as file:
                while True:
                    bytes_file = file.read(max_size_file)
                    if not bytes_file:
                         await server_sio.emit('end_file', data={'iter': iter}, namespace=self.namespace)
                         break
                    encoded_bytes_file = base64.b64encode(bytes_file)
                    await server_sio.emit('recv_tables', data={'file': encoded_bytes_file}, namespace=self.namespace)
                    iter += 1
        

    async def on_get_data_cajas(self, data: dict):
         pass

    async def on_update_tablas(self, sid):
       server_sio.start_background_task(self.start_task)

    async def on_connect(self, sid, environ):
        self.headers_client_serie = environ['asgi.scope']['headers'][1][1].decode('utf-8')
        if len(connected_clients) > 0 :
             for clients in connected_clients:
                  if self.headers_client_serie in clients.values():
                       await server_sio.emit('disconnect_license', to=sid, data={'message': 'The license has already been registered on the server'}, namespace='/default')
                       print('cliente ya, conectado', sid)
        
        #gt =await server_sio.handle_request()     
        #print(gt)
        connected_clients.append({sid: self.headers_client_serie})
        print(connected_clients)
        
    async def on_disconnect(self, sid):
         for i in connected_clients:
              if sid in i.keys():
                connected_clients.remove(i)
         print(connected_clients)       
             
server_sio.register_namespace(NamespaceServer('/default')) 
server_sio.register_namespace(NamespaceServer('*'))          
         

# for serie in getKeys():#Obteniendo series disponibles de las cajas, y creando instancias de namespaces
#     if serie != None:
#         server_sio.register_namespace(NamespaceServer(f"/{serie.upper()}"))


if __name__ == '__main__':
    if not os.path.exists(f"{pathlib.Path().absolute()}\\tmp"):
            os.mkdir(f"{pathlib.Path().absolute()}\\tmp")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
            os.mkdir(f"{pathlib.Path().absolute()}\\zip")        

    uvicorn.run(app, host='127.0.0.1', port=8000)

