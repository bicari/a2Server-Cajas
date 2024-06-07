import socketio
import os
import time
import asyncio
import socketio.exceptions
import pathlib
from read_ini import getConfigClient

caja = socketio.AsyncClient( reconnection=True, logger=True)
config =  getConfigClient()

async def search_sales():
    while caja.connected:
        print('hola')
        await asyncio.sleep(3)

@caja.on('connect', namespace=f'/{config[2].upper()}')
async def connect():
    try:
        print('Estoy conectado')
        await asyncio.sleep(5)
        caja.start_background_task(search_sales)

        await caja.emit('start_task', data={'hola':1},namespace=f"/{config[2].upper()}")
    except socketio.exceptions.ConnectionError:
        print('reconectando')
        await asyncio.sleep(5)
        

async def init_client():
    try:
        await caja.connect(f'http://{config[0]}:{config[1]}', namespaces=f'/{config[2].upper()}', headers={'name': f'/{config[2].upper()}', 'serie': f'{config[3].upper()}'}, transports=['polling', 'websocket'])
        await caja.wait()
    except Exception as e:    
        while not caja.connected:
            try:
                await caja.connect(f'http://{config[0]}:{config[1]}', namespaces=f'/{config[2].upper()}', headers={'name': f'/{config[2].upper()}', 'serie': f'{config[3].upper()}'}, transports=['polling', 'websocket'])
                await caja.wait()
            except Exception as e:
                print(e)
                time.sleep(3)    

if __name__ == '__main__':
    if not os.path.exists(f"{pathlib.Path().absolute()}\\tmp"):
        os.mkdir(f"{pathlib.Path().absolute()}\\tmp")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
        os.mkdir(f"{pathlib.Path().absolute()}\\zip") 
    asyncio.get_event_loop().run_until_complete(init_client())