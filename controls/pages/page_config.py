import flet as ft
from pathlib import Path
import os
class ConfigPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.text_field_ruta_local = ft.TextField('Ruta local', label='Ruta a2Cash Local' , max_length=100, offset=ft.Offset(0,0.2), border_radius=12, width=250, on_change=self.on_change)
        self.text_field_IP = ft.TextField('', label='Server IP',  max_length=100,  offset=ft.Offset(0,0.2), on_change=self.on_change)
        self.text_field_SERIE = ft.TextField('Ruta local', label='Serie Caja', max_length=100, offset=ft.Offset(0,0.2))
        self.page.floating_action_button = ft.FloatingActionButton("Guardar", icon=ft.icons.SAVE, visible=True, on_click=self.click_save_data)
        self.column =  ft.Column([self.text_field_ruta_local, self.text_field_IP, self.text_field_SERIE], expand=True)
        self.visible = True
        self.content = self.column
        self.bgcolor = ft.colors.CYAN_800
        self.border_radius = 12
        self.expand = True

    def on_change(self, e: ft.ControlEvent):
       data: ft.TextField = e.control
       if not e.data.isdigit() and data.label == 'Server IP':
               self.text_field_IP.value = ''
       if not os.path.isdir(e.data):
           print('this path dosent exists')
           self.message_error_type_data_field = ft.SnackBar(ft.Text('Solo se admiten datos numericos en este campo'), visible=True, duration=4000)
           self.message_error_type_data_field.open = True
           self.page.overlay.append(self.message_error_type_data_field)
           self.page.update()
    
    def click_save_data(self, e: ft.ControlEvent):
        print(self.text_field_ruta_local.value)
        self.text_field_ruta_local.value = ''
        self.message_save_data = ft.SnackBar(ft.Text('Cambios guardados con éxito!') ,action='Alright!', visible=True, duration=4000)
        self.message_save_data.open = True
        self.page.overlay.append(self.message_save_data)
        self.page.update()
        



            
