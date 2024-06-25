import socketio
import os
import time
import asyncio
import socketio.exceptions
import pathlib
from read_ini import getConfigClient
import base64
import sys
from querys.update_tablas import sqlQuerys
from flet import Page

caja = socketio.AsyncClient( reconnection=True, logger=True)
config =  getConfigClient()
list_file = []
print(config)
async def search_sales():
    while caja.connected:
        await asyncio.sleep(3)
        auto = sqlQuerys('A2GKC').search_sales(auto=config[2],serie=config[3])
       
            


@caja.on('message', namespace='/default')
async def message(data):
    print(data)

#Evento de desconexion en caso de que duplicacion de licencia
@caja.on('disconnect_license', namespace='/default')
async def disconnect_from_server(data):
   print(data)
   await caja.disconnect()
   sys.exit(0)
   

@caja.on('recv_tables', namespace='/default')
async def decompress_data(data: dict):
    print(data.keys())
    list_file.append(base64.b64decode(data['file']))#Decodificando partes de archivo segun codificacion base64
    print(len(list_file))

@caja.on('end_file', namespace='/default')
async def end_file(data: dict):
    if data['iter'] == len(list_file):       
        file = b''.join(list_file)#Uniendo fragmentos de bytes de los archivos a un solo archivo
        with open('zip\\data_partes.zip', 'wb') as file_zip:
            file_zip.write(file)#Escribiendo archivo comprimido
    list_file.clear()
@caja.on('update_inventario', namespace='*')
async def update_sinvdep(data: dict):
    print(data, 'test')


@caja.on('connect', namespace='/default')
async def connect():
    try:
        print('Estoy conectado')
        await asyncio.sleep(5)
        caja.start_background_task(search_sales)
        await caja.emit('update_tablas', namespace='/default')
    except socketio.exceptions.ConnectionError:
        print('reconectando')
        await asyncio.sleep(5)
        

async def init_client(page: Page):
    try:
        await caja.connect(f'http://{config[0]}:{config[1]}', namespaces='/default', headers={'serie': f'{config[3].upper()}'}, transports=['polling', 'websocket'])
        await caja.wait()
    except Exception as e:    
        while not caja.connected:
            try:
                await caja.connect(f'http://{config[0]}:{config[1]}')
                await caja.wait()
            except Exception as e:
                print(e)
                time.sleep(3)    

if __name__ == '__main__':
    if not os.path.exists(f"{pathlib.Path().absolute()}\\tmp"):
        os.mkdir(f"{pathlib.Path().absolute()}\\tmp")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
        os.mkdir(f"{pathlib.Path().absolute()}\\zip") 
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
        os.mkdir(f"{pathlib.Path().absolute()}\\db")     
    asyncio.get_event_loop().run_until_complete(init_client())