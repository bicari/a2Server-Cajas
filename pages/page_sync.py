import flet as ft
from socketio import AsyncClient
import asyncio
class SyncPage(ft.Container):
    def __init__(self, page: ft.Page, client_socket: AsyncClient, list_view_send_data: ft.ListView, progress_ring: ft.ProgressRing):
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

    async def emit_send_data(self):#Funcion asincrona(Corrutina) que emite el evento de envio de datos al server
        try:
            await self.async_client.emit('update_so_sd_local', namespace='/default')
            self.container_list_view.visible = True
            self.list_view_data.controls.append(ft.Text('Ejecutando solicitud, esperando respuesta del servidor'))
            self.page.overlay.append(ft.Column(controls=[self.progress_ring], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END, expand=True, width=650))
            self.send_message.content = self.progress_ring
            
            
            
            self.page.update()
        except Exception as e:
             self.send_message.content = ft.Text('Error de transmision, no conectado al servidor {}'.format(e))
             self.send_message.open = True
             self.page.overlay.append(self.send_message)
             self.page.update()   
             

    def entry_emit_send_data(self):#Entrada a la funcion asincrona
        asyncio.run(self.emit_send_data())    

    def clic_btn_sync_data(self, e):
        self.entry_emit_send_data()
       