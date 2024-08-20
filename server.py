import socketio
import asyncio
import pathlib
import uvicorn.server
import uvicorn.config
import os, sys
import base64
from datetime import datetime
from functions import getKeys, getServerConfig
from querys import sqlQuerys

from functions import search_database_files, decompress_file

server_sio = socketio.AsyncServer(async_mode='asgi',  logger=True, always_connect=False, cors_allowed_origins = '*', Engineio_logger=True, ping_timeout=60, ping_interval=30)
app = socketio.ASGIApp(server_sio)
connected_clients = list()
lists_file_clients = []
tasks = []
part_file = []
config = getServerConfig()

class NamespaceServer(socketio.AsyncNamespace):
    def __init__(self, namespace):
        super().__init__(namespace)
        self.namespace = namespace #Espacio de nombre general
        if config[3] != str(datetime.date(datetime.now())):#Validando ultima fecha de compactacion de datos si no es igual a la actual
          asyncio.create_task(search_database_files(catalogname=config[2]))
          asyncio.create_task(self.start_task())


    async def on_recv_data_tables_client(self, sid, data:dict):
         lists_file_clients.append(base64.b64decode(data['file']))#Decodificando partes de archivo segun codificacion base64

     #Evento de finalizacion de compresion de archivo enviado por el cliente al servidor
    async def on_end_file_client(self, sid, data):
          if data['iter_client'] == len(lists_file_clients):
               file = b''.join(lists_file_clients)#Uniendo fragmentos de bytes de los archivos a un solo archivo
               with open('zip\\data_partes_ventas_{sid}.zip'.format(sid=sid), 'wb') as file_zip:
                    file_zip.write(file)#Escribiendo archivo comprimido
               if os.path.isfile('zip\\data_partes_ventas_{sid}.zip'.format(sid=sid)):
                    await decompress_file('zip\\data_partes_ventas_{sid}.zip'.format(sid=sid), path_decompress='zip_backup\\')
               await sqlQuerys('DSN=A2GKC;CatalogName={catalogname}'.format(catalogname=config[2])).insert_into_data_server()     
               await server_sio.emit('clear_data_local', to=sid, namespace='/default')     
          lists_file_clients.clear()


    async def start_task(self):
        max_size_file = 1024*1024
        iter = 0 
        if os.path.isfile('data.zip') == True and datetime.fromtimestamp(os.path.getmtime('data.zip')).strftime("%Y-%m-%d") == str(datetime.date(datetime.now())):#Verificando que exista el archivo data.zip y su ultima fecha de modificacion sea hoy
            #size_file = os.path.getsize('data.zip')
            with open('data.zip', 'rb') as file:
                while True:
                    bytes_file = file.read(max_size_file)
                    if not bytes_file:
                         #await server_sio.emit('end_file', data={'iter': iter}, namespace=self.namespace)
                         print('Archivo por partes en memoria', len(part_file))
                         break
                    encoded_bytes_file = base64.b64encode(bytes_file)
                    part_file.append(encoded_bytes_file)
                    #await asyncio.sleep(0.9)
                    #await server_sio.emit('recv_tables', data={'file': encoded_bytes_file}, namespace=self.namespace)
                    iter += 1
         
    async def send_data_file_client(self, sid):
         iter = 0
         for part in part_file:
              await server_sio.emit('recv_tables',data={'file': part}, namespace=self.namespace, to=sid)
              iter +=1 
         await server_sio.emit('end_file', data={'iter':iter}, namespace=self.namespace, to=sid)
          
    async def on_update_so_sd_local(self, sid):
         MAXAUTO = await sqlQuerys('DSN=A2GKC;CatalogName={catalogname}'.format(catalogname=config[2])).max_Auto()
         if type(MAXAUTO) == Exception:
               await server_sio.emit('update_so_sd', data={'soperacion_auto': 'error', 'sdetalle_auto': 'error'}, to=sid, namespace='/default')
         else:
               await server_sio.emit('update_so_sd', data={'soperacion_auto': MAXAUTO[0], 'sdetalle_auto': MAXAUTO[1]}, to=sid, namespace='/default')    

    async def on_succes_update_local(self, sid, data: dict):
         if data['type'] == True:
              await server_sio.emit('send_data_sales', data={}, to=sid, namespace='/default')
         else:
              await server_sio.emit('send_data_faile', data={}, to=sid, namespace='/default')     

    async def on_update_tablas(self, sid):
       #server_sio.start_background_task(self.start_task)
       tarea = asyncio.create_task(self.send_data_file_client(sid=sid))
       tasks.append(tarea)
       if len(tasks) > 0:
           result = await asyncio.gather(*tasks)
           for a in result:
                print(a)
           tasks.clear()     


    #async def on_disconnect_user(self, sid):
     #    await server_sio.disconnect(sid=sid)
     #    for i in connected_clients:
     #         if sid in i.keys():
     #           connected_clients.remove(i)
     #    print(connected_clients)        
     #    print(f'user {sid} desconectado')  

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
         
         

# for serie in getKeys():#Obteniendo series disponibles de las cajas, y creando instancias de namespaces
#     if serie != None:
#         server_sio.register_namespace(NamespaceServer(f"/{serie.upper()}"))


if __name__ == '__main__':
    if not os.path.exists(f"{pathlib.Path().absolute()}\\tmp"):
            os.mkdir(f"{pathlib.Path().absolute()}\\tmp")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
            os.mkdir(f"{pathlib.Path().absolute()}\\zip")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip_backup"):
            os.mkdir(f"{pathlib.Path().absolute()}\\zip_backup")                      

    uvicorn.run(app, host='127.0.0.1', port=8000)
     
