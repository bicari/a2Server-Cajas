import socketio
import asyncio
import pathlib
import socketio.exceptions
import os
import base64
#from datetime import datetime
from functions import  getServerConfig
from querys import sqlQuerys
from functions import decompress_file

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

    async def on_update_ssistema_serie(self, sid, data):
         """Funcion que actualiza el numero de correlativo de facturacion en la tabla Ssistema, y luego emite un evento de actualizacion
          en las cajas para actualizar de forma local el correlativo de cada serie de facturación """
         sqlQuerys('DSN=A2GKC;CatalogName={catalogname}'.format(catalogname=config[2])).update_ssistema_document_number(data=data)   
   
    
         
         
    async def send_data_file_client(self, sid):
          await server_sio.emit('recv_tables', namespace=self.namespace, to=sid)

          
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

    async def on_connect(self, sid, environ):
        self.headers_client_serie = environ['HTTP_SERIE']
        print(self.headers_client_serie)
        if len(connected_clients) > 0 :
             for clients in connected_clients:
                  if self.headers_client_serie in clients.values():
                       await server_sio.emit('disconnect_license', to=sid, data={'message': 'The license has already been registered on the server'}, namespace='/default')
                       print('cliente ya, conectado', sid)
        
        #gt =await server_sio.handle_request()     
        #print(gt)
        connected_clients.append({sid: self.headers_client_serie})
        print(connected_clients, self.headers_client_serie)
        
    async def on_disconnect(self, sid):
         try:
               for i in connected_clients:
                 if sid in i.keys():
                    connected_clients.remove(i)
               print(connected_clients)
         except Exception as e: 
              print(e)            

async def correlativos():
     data=sqlQuerys('DSN=A2GKC;CatalogName={catalogname}'.format(catalogname=config[2])).get_correlativos()
     ini = True
     while True:
          if len(connected_clients):
               data=sqlQuerys('DSN=A2GKC;CatalogName={catalogname}'.format(catalogname=config[2])).get_correlativos()
          await asyncio.sleep(6)
          if ini:
               series = {}
               for x in data:
                    series[x[1]] = x[0]
               ini = False
          for x in data:
               if x[0] > series[x[1]] :
                    await server_sio.emit('update_correlativo', data={'Serie' :x[1],'Correlativo': x[0]}, namespace='/default')
                    series[x[1]] = x[0]
                    
               
          
          

server_sio.register_namespace(NamespaceServer('/default'))
server_sio.start_background_task(correlativos)

         
         

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

     
