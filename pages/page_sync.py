import flet as ft
from socketio import Client
import asyncio
import datetime
from querys import sqlQuerys
from functions import getConfigClient
import time
config  = getConfigClient()
PATH_DSN_ODBC =r"""DSN=A2GKC;DRIVER={path};ConnectionType=Local;RemoteIPAddress=127.0.0.1;RemotePort=12005;RemoteCompression=0;
RemotePing=False;RemotePingInterval=60;RemoteEncryption=False;RemoteEncryptionPassword=elevatesoft;RemoteReadAhead=50;CatalogName={catalogname};ReadOnly=False;
LockRetryCount=15;LockWaitTime=100;ForceBufferFlush=False;
StrictChangeDetection=False;PrivateDirectory={catalogname}""".format(catalogname=config[2], path=r'C:\Program Files (x86)\DBISAM 4 ODBC-CS\libs\dbodbc\read-write\win64\dbodbc.dll')
class SyncPage(ft.Container):
    def __init__(self, page: ft.Page, client_socket: Client, list_view_send_data: ft.ListView, progress_ring: ft.ProgressRing):
        super().__init__()
        self.page = page
        self.list_view_data = list_view_send_data
        self.container_list_view =  ft.Container(self.list_view_data, border_radius=12,  expand=True, visible=False, gradient=ft.LinearGradient(begin=ft.alignment.top_center, end=ft.alignment.bottom_center, colors=['#3c3c3c','#515151','#474b4e','#666666']))
        self.container_data_sync = ft.Row([self.list_view_data])
        self.container_sync = ft.Row([ft.Container(ft.Text('Sincronizar', size=15, color='#BEBEBE'), 
                                                   border_radius=10, alignment=ft.alignment.center_left, bgcolor='#2c2c2c', height=60, expand=True)], offset=ft.Offset(0, 0.1))
        self.send_data_to_server = ft.IconButton(ft.icons.SEND_AND_ARCHIVE_ROUNDED, icon_color=ft.colors.GREEN_300, icon_size=60, tooltip='Enviar datos al servidor', on_click=self.clic_btn_sync_data)
        self.content = ft.Column([self.container_sync, self.send_data_to_server, self.container_list_view], expand=True)
        self.expand = True
        self.border_radius = 10
        self.bgcolor = '#474b4e'
        self.visible = False
        self.async_client = client_socket
        self.send_message = ft.SnackBar(ft.Text(), visible=True, duration=4000, bgcolor=ft.colors.RED_300)
        self.progress_ring = progress_ring
        self.modal_dialog = ft.AlertDialog(modal=True, title=ft.Text('Por favor confirme'), content=ft.Text('Desea enviar datos al server?'), actions=[ft.ElevatedButton('Sí', on_click=self.entry_emit_send_data
                                                                                                                                                                    ), ft.OutlinedButton('No', on_click=self.modal_no_click)],
                                                                                                                                                                    actions_alignment=ft.MainAxisAlignment.END)
        self.column_progress_ring = ft.Column(controls=[self.progress_ring],alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END, expand=True, width=650)
    def emit_send_data(self):#Funcion asincrona(Corrutina) que emite el evento de envio de datos al server
        try:
            self.container_list_view.visible = True
            self.list_view_data.controls.append(ft.Text('{hora} Ejecutando solicitud, esperando respuesta del servidor'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
            #self.page.overlay.append(ft.Column(controls=[self.progress_ring], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END, expand=True, width=650))
            #self.page.overlay.append(self.column_progress_ring)
            self.page.update()
            time.sleep(5)
            if sqlQuerys(PATH_DSN_ODBC).get_data_local(config[3]) > 0:
                self.async_client.emit('update_so_sd_local', namespace='/default')
            else:
                self.list_view_data.controls.append(ft.Text('{hora} Tablas locales sin datos para enviar'.format(hora=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), color= ft.colors.RED_400))   
                self.progress_ring.visible = False
                self.page.update()
        except Exception as e:
             self.send_message.content = ft.Text('Error de transmision, no conectado al servidor {}'.format(e))
             self.send_message.open = True
             self.page.overlay.append(self.send_message)
             self.page.update()   
             

    def entry_emit_send_data(self, e):#Entrada a la funcion asincrona
        self.modal_dialog.open = False
        self.page.update()
        self.emit_send_data()
    
    def modal_no_click(self, e):
        self.modal_dialog.open = False
        self.page.update()
        
        
        

    def clic_btn_sync_data(self, e):
        self.modal_dialog.visible = True
        self.modal_dialog.open = True
        self.page.open(self.modal_dialog)
        self.page.update()
        
       