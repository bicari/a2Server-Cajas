import flet as ft
from PIL import Image
import asyncio
import datetime
#from client_cajas import init_client, caja
import socketio
import os, signal,sys
import time
import asyncio
import socketio.exceptions
from controls import GrupoContenedores
import pathlib
from functions import getConfigClient
import base64
import sys
from querys.update_tablas import sqlQuerys
from tray_icon import Icon
from pages import ConfigPage, SyncPage
from querys import sqlQuerys


 
p : ft.Page
caja = socketio.AsyncClient( reconnection=True, logger=True)
list_file = []
config =  getConfigClient()
PATH_DSN_ODBC =r"""DSN=A2GKC;DRIVER={path};ConnectionType=Local;RemoteIPAddress=127.0.0.1;RemotePort=12005;RemoteCompression=0;
RemotePing=False;RemotePingInterval=60;RemoteEncryption=False;RemoteEncryptionPassword=elevatesoft;RemoteReadAhead=50;CatalogName={catalogname};ReadOnly=False;
LockRetryCount=15;LockWaitTime=100;ForceBufferFlush=False;
StrictChangeDetection=False;PrivateDirectory={catalogname}""".format(catalogname=config[2], path=r'C:\Program Files (x86)\DBISAM 4 ODBC-CS\libs\dbodbc\read-write\win64\dbodbc.dll')

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

@caja.on('update_so_sd', namespace='/default')
async def update_soperacion_sdetalle_local(data:dict):
    await caja.sleep(2.5)
    list_view_data_client.controls.append(ft.Text('{hora} Recibiendo datos del servidor'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    list_view_data_client.controls.append(ft.Text('{hora} Ejecutando actualizacion'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    list_view_data_client.controls.append(ft.Text('{hora} Actualizacion realizada'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    list_view_data_client.controls.append(ft.Text('{hora} Preparado para enviar datos'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    await caja.emit('succes_update_local', data={'type': True}, namespace='/default')
    list_view_data_client.controls.append(ft.Text('{hora} Enviando datos, por favor espere'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    p.update()
    auto_so = data['soperacion_auto']
    auto_sd = data['sdetalle_auto']
    print(auto_sd)
    #result = sqlQuerys(dsn=PATH_DSN_ODBC).update_tablas_locales(auto_so, auto_sd)

@caja.on('send_data_sales', namespace='/default')
async def send_files_sales(data: dict):
    list_view_data_client.controls.append(ft.Text('2023-02-16 14:30:45 datos enviados con éxito'))
    progress_ring.visible = False
    
    p.update()    

@caja.on('connect', namespace='/default')
async def connect():
    badge_connection.bgcolor = 'green'
    snack_bar_msg_connection.content = ft.Text('Conectado al servidor')
    snack_bar_msg_connection.open = True
    snack_bar_msg_connection.bgcolor = ft.colors.GREEN_300
    p.update()
    tray_icon_minimize.icon = Image.open("assets\\Conectado.png")
    try:
        print('Estoy conectado')
        #caja.start_background_task(search_sales)
        #await caja.emit('update_tablas', namespace='/default')
    except socketio.exceptions.ConnectionError:
        print('reconectando')
        await asyncio.sleep(5)

@caja.on('disconnect', namespace='/default')
async def disconnect():
    badge_connection.bgcolor = 'red'
    snack_bar_msg_connection.content = ft.Text('Desconectado del servidor')
    snack_bar_msg_connection.open = True
    p.update()
    tray_icon_minimize.icon = Image.open("assets\\Desconectado.png")    

async def init_client():
    try:
        
        await caja.connect(f'http://{config[0]}:{config[1]}', namespaces='/default', headers={'serie': f'{config[3].upper()}'}, transports=['polling', 'websocket'])
        await caja.wait()
       
    except Exception as e:    
        while not caja.connected:
            try:
                await caja.connect(f'http://{config[0]}:{config[1]}', namespaces='/default', headers={'serie': f'{config[3].upper()}'}, transports=['polling', 'websocket'])
                await caja.wait()
            except Exception as e:
                print(e)
                time.sleep(3)    
      


def window_event(e):
    print(e)
    if e.data == 'minimize':
        p.window.skip_task_bar = True
        tray_icon_minimize.visible = True
        p.update() 
    if e.data == 'close':
        confirm_close_dialog.open = True
        p.overlay.append(confirm_close_dialog)
        p.open(confirm_close_dialog)
        print('eee')
        p.update()
    
            
    

async def close_window(e):
    print('cerrado')   

async def modal_yes_click(e):
    #await caja.emit(event='disconnect_user', namespace='/default')
    await caja.disconnect()
    p.window.destroy()
 
    
    
    

def modal_no_click(e):
    confirm_close_dialog.open = False
    p.update()

async def main(page):
    global p
    p = page
    
    global tray_icon_minimize, confirm_close_dialog
    confirm_close_dialog = ft.AlertDialog(modal=True, title=ft.Text('Por favor confirme'), content=ft.Text('Desea cerrar la app?'), actions=[ft.ElevatedButton('Sí', on_click=modal_yes_click
                                                                                                                                                                    ), ft.OutlinedButton('No', on_click=modal_no_click)],
                                                                                                                                                                    actions_alignment=ft.MainAxisAlignment.END)
    tray_icon_minimize = Icon( title='App de sincronizacion', icon=Image.open("assets\\Desconectado.png"), page=p)
    p.window.max_height = 400
    p.window.min_height= 400
    p.window.min_width= 400
    p.window.prevent_close = True
    #p.run_thread(entry_connect)
    p.window.on_event = window_event
    p.theme_mode = ft.ThemeMode.DARK
    print(p.window.height, p.window.width)
    p.window.maximizable = False
    p.window.resizable = False
    #global hilo_connect
    #hilo_connect = threading.Thread(target=entry_connect) 
    #hilo_connect.start()
    #print(hilo_connect.name, hilo_connect.native_id)
    global badge_connection
    global snack_bar_msg_connection, list_view_data_client, progress_ring
    progress_ring = ft.ProgressRing(width=60, height=60, stroke_width=6, color=ft.colors.GREEN_300)
    list_view_data_client = ft.ListView([], spacing=10, padding=20, auto_scroll=True)
    snack_bar_msg_connection = ft.SnackBar(ft.Text() ,action='Alright!', visible=True, duration=4000)#Mensaje de conexion al servidor establecida
    p.overlay.append(snack_bar_msg_connection)
    badge_connection = ft.Badge(content=ft.Icon(ft.icons.ONLINE_PREDICTION), bgcolor=ft.colors.RED, alignment=ft.alignment.center,small_size=10)
    btn_save_data = ft.FloatingActionButton("Guardar", icon=ft.icons.SAVE, visible=False)  
    page_config = ConfigPage(page=p, config=config, btn_save_data=btn_save_data)
    sync_page = SyncPage(page=p, client_socket=caja, list_view_send_data=list_view_data_client, progress_ring=progress_ring)
    buttons_sidebar= GrupoContenedores(page=p, badge=badge_connection, page_container_to_show_settings=page_config, page_container_to_show_sync=sync_page).control_group
    
    
   
    
    
   
    p.add(
            ft.Row(controls=[
            ft.Container(
                ft.Column(controls=buttons_sidebar, horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=80,expand=True), 
                bgcolor='#474b4e', border_radius=12),
            page_config,
            sync_page
                
            ],
            expand=True
            #ft.Row([ft.Container(bgcolor='white', expand=True)], expand=True)
          )     
         
        
    )
    
    await init_client()
if __name__ == '__main__':
    #tray_icon_minimize.run_detached(setup=my_setup)
    if not os.path.exists(f"{pathlib.Path().absolute()}\\tmp"):
        os.mkdir(f"{pathlib.Path().absolute()}\\tmp")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
        os.mkdir(f"{pathlib.Path().absolute()}\\zip") 
    ft.app(main)
    
     

