import flet as ft
from PIL import Image
import datetime
#from client_cajas import init_client, caja
import socketio
import os, sys
import time
import asyncio
import socketio.exceptions
from controls import GrupoContenedores
import pathlib
from functions import getConfigClient, search_local_tables, decompress_file_sinc, show_message_powershell, saveSyncData
import base64
import sys
from querys.update_tablas import sqlQuerys
from tray_icon import Icon
from pages import ConfigPage, SyncPage
from querys import sqlQuerys
from querys.create_tablas import SOPERACIONINV, SDETALLEVENTA, SDETALLEINV, STRANSBANCO,SCUENTASXCOBRAR,SDETALLECOMPRA,SDETALLEPARTES,STRANSCUENTA 
import requests
import json 
p : ft.Page
caja = socketio.Client(reconnection=True, logger=True)
list_file = [] 
click_disconnect = False
reconnection = False
tasks = []
config =  getConfigClient()
PATH_DSN_ODBC =r"""DSN=A2GKC;DRIVER={path};ConnectionType=Local;RemoteIPAddress=127.0.0.1;RemotePort=12005;RemoteCompression=0;
RemotePing=False;RemotePingInterval=60;RemoteEncryption=False;RemoteEncryptionPassword=elevatesoft;RemoteReadAhead=50;CatalogName={catalogname};ReadOnly=False;
LockRetryCount=15;LockWaitTime=100;ForceBufferFlush=False;
StrictChangeDetection=False;PrivateDirectory={catalogname}""".format(catalogname=config[2], path=r'C:\Program Files (x86)\DBISAM 4 ODBC-CS\libs\dbodbc\read-write\win64\dbodbc.dll')
LOCK_FILE = 'app.lock'



@caja.on('update_correlativo', namespace='/default')
def actualizar_correlativo_local(data: dict):
    sqlQuerys(PATH_DSN_ODBC).update_correlativos(serie=data['Serie'], correlativo=data['Correlativo'])
    

   

#Evento de desconexion en caso de que duplicacion de licencia
@caja.on('disconnect_license', namespace='/default')
def disconnect_from_server(data):
   print(data)
   caja.disconnect()
   sys.exit(0)
   
def save_data_in_list(data):
    list_file.append(base64.b64decode(data['file']))
    print(len(list_file))

@caja.on('recv_tables', namespace='/default')
def decompress_data():
    try:
        response_token = requests.post('http://{ip}:{port}/token/'.format(ip=config[8],port=config[9]), 
                                   headers={'user':'{caja}'.format(caja=config[3]), 'password':'bic@ri3103*'})
        if response_token.status_code == 200:
            token = json.loads(response_token.content)
            response = requests.get('http://{ip}:{port}/download_file/'.format(ip=config[8], port=config[9]), 
                                headers={'Authorization': 'Bearer {token}'.format(token=token['token'])},stream=True)
            with open('zip\\data_cajas_{serie}.zip'.format(serie=config[3]), 'wb') as file:
                for part_file in response.iter_content(chunk_size=4096):
                    if part_file:
                        file.write(part_file)            
    except requests.exceptions.ConnectionError as e:
        snack_bar_msg_connection.content = ft.Text(f'Error al intentar sincronizar datos, verifique la disponibilidad del servidor: {e}')
        snack_bar_msg_connection.open = True
        snack_bar_msg_connection.bgcolor = ft.colors.RED_300
        snack_bar_msg_connection.duration = 4500

    if os.path.exists('zip\\data_cajas_{serie}.zip'.format(serie=config[3])):
        if decompress_file_sinc('zip\\data_cajas_{serie}.zip'.format(serie = config[3]), config[2]):
            snack_bar_msg_connection.content = ft.Text('Sincronización inicial culminada, data actualizada')
            snack_bar_msg_connection.open = True
            snack_bar_msg_connection.bgcolor = ft.colors.GREEN_300
            p.update()
               #llamando a funcion que actualiza la tabla susuarios con los directorios locales
            sqlQuerys(PATH_DSN_ODBC).update_susuarios(config[2])
            saveSyncData(datetime.datetime.now().strftime("%Y-%m-%d"))

#Evento de sincronizacion de tablas al iniciar la app
@caja.on('end_file', namespace='/default')
def end_file(data: dict):    
    if os.path.isfile('zip\\data_partes_{sid_caja}.zip'.format(sid_caja=caja.sid)):
        if decompress_file_sinc('zip\\data_partes_{sid_caja}.zip'.format(sid_caja = caja.sid), config[2]):
               snack_bar_msg_connection.content = ft.Text('Sincronización inicial culminada, data actualizada')
               snack_bar_msg_connection.open = True
               snack_bar_msg_connection.bgcolor = ft.colors.GREEN_300
               p.update()
               #llamando a funcion que actualiza la tabla susuarios con los directorios locales
               sqlQuerys(PATH_DSN_ODBC).update_susuarios(config[2])
               saveSyncData(datetime.datetime.now().strftime("%Y-%m-%d"))
    list_file.clear()

@caja.on('update_inventario', namespace='*')
def update_sinvdep(data: dict):
    print(data, 'test')

@caja.on('clear_data_local', namespace='/default')
def clear_data_local():
    result = sqlQuerys(PATH_DSN_ODBC).clear_tablas_locales()
    if result:
        list_view_data_client.controls.append(ft.Text('{hora} Tablas locales de operaciones han sido despejadas'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    else:
        list_view_data_client.controls.append(ft.Text('{hora} ERROR:Tablas locales no han sido despejadas'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), color=ft.colors.RED_300))    
    p.update()


@caja.on('update_so_sd', namespace='/default')
def update_soperacion_sdetalle_local(data:dict):
    caja.sleep(2.5)
    list_view_data_client.controls.append(ft.Text('{hora} Recibiendo datos del servidor'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    list_view_data_client.controls.append(ft.Text('{hora} Ejecutando actualizacion'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    p.update()
    result_query = sqlQuerys(PATH_DSN_ODBC).update_tablas_locales(auto_sd=data['sdetalle_auto'], auto_so=data['soperacion_auto'])
    if result_query:
        caja.emit('succes_update_local', data={'type': True}, namespace='/default')
        list_view_data_client.controls.append(ft.Text('{hora} Actualizacion realizada'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        list_view_data_client.controls.append(ft.Text('{hora} Preparado para enviar datos'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        p.update()
    else:    
        progress_ring.visible = False
        snack_bar_msg_connection.content = ft.Text(result_query)
        snack_bar_msg_connection.open = True
        snack_bar_msg_connection.bgcolor = ft.colors.RED_300
        p.update()    
   

@caja.on('send_data_sales', namespace='/default')
def send_files_sales(data: dict):
    
    list_view_data_client.controls.append(ft.Text('{hora} Enviando datos, por favor espere'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    if search_local_tables(config[2], caja.sid) == True: #Buscando tablas locales para enviar al server
        iter = 0
        try:
            with open(f'zip\\data_ventas_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-")}.zip', 'rb') as file:
                while True:
                    bytes_file_sales = file.read(1024*1024)
                    if not bytes_file_sales:
                        caja.emit('end_file_client', data={'iter_client': iter}, namespace='/default')
                        list_view_data_client.controls.append(ft.Text('{hora} datos enviados con éxito'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
                        break
                    encoded_bytes = base64.b64encode(bytes_file_sales)
                    caja.emit('recv_data_tables_client',  data={'file': encoded_bytes}, namespace='/default')
                    iter += 1
        except Exception as e:
            print(e)            
    progress_ring.visible = False
    p.update()    

@caja.on('connect', namespace='/default')
def connect():
    global reconnection
    config =  getConfigClient()
    if reconnection and int (config[10]) == 1:
        if sqlQuerys(PATH_DSN_ODBC).get_data_local(config[3]) > 0:
            no_factura = sqlQuerys(PATH_DSN_ODBC).get_serie_document_number(config[3])
            no_factura_server = sqlQuerys(dsn='DSN=A2GKC;CatalogName={catalogname}'.format(catalogname=config[5])).get_serie_document_number(config[3])
            print(no_factura, no_factura_server)
            if config[3][:3] == '1NF' or config[3][:3] == 'ZNF' and no_factura > no_factura_server:
                caja.emit('update_ssistema_serie', data={'serie': config[3], 'ultima_factura': no_factura},namespace='/default')
            
        show_message_powershell(r'scripts\\reconnection_message.ps1')
        reconnection = False
        sqlQuerys("DSN=A2GKC; CatalogName={catalogname}.".format(catalogname=config[6])).update_sempresas_a2cash(path_data_local=config[5], path_local_formatos_config=os.path.dirname(config[5]))
    badge_connection.bgcolor = 'green'
    snack_bar_msg_connection.content = ft.Text('Conectado al servidor, iniciando sincronización de archivos')
    snack_bar_msg_connection.open = True
    snack_bar_msg_connection.bgcolor = ft.colors.GREEN_300
    p.update()
    tray_icon_minimize.icon = Image.open("assets\\Conectado.png")
    try:
        if config[7] != datetime.datetime.date(datetime.datetime.now()).strftime('%Y-%m-%d'):  
            caja.emit('update_tablas', namespace='/default')
    except socketio.exceptions.ConnectionError:
        print('reconectando')
        time.sleep(5)

@caja.on('disconnect', namespace='/default')
def disconnect():
    if click_disconnect == False and int(config[10]) == 1:
        global reconnection
        badge_connection.bgcolor = 'red'
        snack_bar_msg_connection.content = ft.Text('Desconectado del servidor')
        snack_bar_msg_connection.open = True
        p.window.center()
        p.update()
        tray_icon_minimize.icon = Image.open("assets\\Desconectado.png")
        
            
            
        show_message_powershell(r'scripts\modal_Test.ps1')  
        sqlQuerys('DSN=A2GKC; CatalogName={catalogname}'.format(catalogname=config[6])).update_sempresas_a2cash(path_data_local=config[2], path_local_formatos_config= os.path.dirname(config[2]))
        show_message_powershell(r'scripts\show_message_contingencia.ps1')
        reconnection = True
    else:
        pass
    # while not caja.connected:
    #     print('test')
    #     try:
    #         caja.connect(f'http://{config[0]}:{config[1]}', namespaces='/default', headers={'serie': f'{config[3].upper()}'}, transports=['polling', 'websocket'])
    #         caja.wait()
    #     except Exception as e:
    #         print(e)
    #         asyncio.sleep(3)    

def init_client():
    try:
        
        caja.connect(f'http://{config[0]}:{config[1]}', namespaces='/default', headers={'serie': f'{config[3].upper()}'}, transports=['polling', 'websocket'])
        caja.wait()
       
    except (socketio.exceptions.ConnectionError) as e: 
        while not caja.connected:
                 try:
                     caja.connect(f'http://{config[0]}:{config[1]}', namespaces='/default', headers={'serie': f'{config[3].upper()}'}, transports=['polling', 'websocket'])
                     caja.wait()
                 except Exception as e:
                     time.sleep(2.5) 
        

def window_event(e):
    if e.data == 'minimize':
        p.window.skip_task_bar = True
        tray_icon_minimize.visible = True
        p.update() 
    if e.data == 'close':
        p.open(confirm_close_dialog)
        p.update()
       
    
    
            
    

def close_window(e):
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    p.window.destroy()
    caja.disconnect()  
    os._exit(0)
    
    
   
def modal_yes_click(e):
    #await caja.emit(event='disconnect_user', namespace='/default')
    global click_disconnect
    click_disconnect = True
    close_window(e)
    # try:
    #      pending_tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    #      for task in pending_tasks:
    #          print(task)
    #          task.cancel()
    #          print('cancelando')
    #          await task
    # except Exception as e:
    #      print(e)    
    
    
    

 
    
    
    

def modal_no_click(e):
    # confirm_close_dialog.open = False
    # p.update()
    p.close(confirm_close_dialog)

def main(page):

    

    global p
    p = page
    
    global tray_icon_minimize, confirm_close_dialog, disconnect_modal
    disconnect_modal = ft.AlertDialog(modal=True, title=ft.Text('Desconexión detectada'),  actions=[])
    confirm_close_dialog = ft.AlertDialog(modal=True, title=ft.Text('Por favor confirme'), content=ft.Text('Desea cerrar la app?'), actions=[ft.ElevatedButton('Sí', on_click=modal_yes_click
                                                                                                                                                                    ), ft.OutlinedButton('No', on_click=modal_no_click)]
                                                                                                                                                                    )
    tray_icon_minimize = Icon( title='App de sincronizacion', icon=Image.open("assets\\Desconectado.png"), page=p)
    #p.window.max_height = 400
    #p.window.min_height= 400
    #p.window.min_width= 400
    p.window.prevent_close = True
    #p.run_thread(entry_connect)
    p.window.on_event = window_event
    p.theme_mode = ft.ThemeMode.DARK
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
    snack_bar_msg_connection = ft.SnackBar(ft.Text() ,action='Alright!', visible=True, duration=1500)#Mensaje de conexion al servidor establecida
    p.overlay.append(snack_bar_msg_connection)
    badge_connection = ft.Badge(content=ft.Icon(ft.icons.ONLINE_PREDICTION), bgcolor=ft.colors.RED, alignment=ft.alignment.center,small_size=10)
    btn_save_data = ft.FloatingActionButton("Guardar", icon=ft.icons.SAVE, visible=False)  
    page_config = ConfigPage(page=p, config=config, btn_save_data=btn_save_data, message_bar=snack_bar_msg_connection)
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
    init_client()

def show_app_running_dialog(page: ft.Page):
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("La aplicación ya está en ejecución"),
        content=ft.Text("Por favor, cierre la otra instancia antes de abrir una nueva."),
        actions=[ft.TextButton("OK", on_click=lambda e: page.window_close())],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()


def check_if_running():
    # Intentamos abrir un puerto específico en el localhost
    if os.path.exists(LOCK_FILE):
        return True
    else:
        with open(LOCK_FILE, 'w') as file:
            file.write('bloqueado')
        return False        
    
    
# async def entry_app():
#     task= asyncio.create_task(ft.app_async(main))
#     await task

if __name__ == '__main__':
    #tray_icon_minimize.run_detached(setup=my_setup)
    sqlQuerys('DSN=A2GKC; CatalogName={catalogname}'.format(catalogname = config[2])).create_tables_locales(tables=(SOPERACIONINV, SDETALLEINV, SDETALLEVENTA, STRANSBANCO,SCUENTASXCOBRAR,SDETALLECOMPRA,SDETALLEPARTES,STRANSCUENTA))
    if not os.path.exists(f"{pathlib.Path().absolute()}\\tmp"):
        os.mkdir(f"{pathlib.Path().absolute()}\\tmp")
    if not os.path.exists(f"{pathlib.Path().absolute()}\\zip"):
        os.mkdir(f"{pathlib.Path().absolute()}\\zip") 
    if check_if_running():        
        ft.app(target=show_app_running_dialog)
        sys.exit()  # Salimos del script
    else:
        ft.app(main)
        
    if os.path.exists(LOCK_FILE):        
        os.remove(LOCK_FILE)    
     

