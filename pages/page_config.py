import flet as ft
import re
import os
from functions import saveInitConfig
class ConfigPage(ft.Container):
    def __init__(self, page: ft.Page, config, btn_save_data: ft.FloatingActionButton):
        super().__init__()
        self.init_config = config # [0]IP [1]PORT [2]rutalocal [3]SERIEACTUAL [4]SERIES
        self.page = page
        self.text_field_ruta_local = ft.TextField(config[2], label='Ruta a2Cash Local', max_length=100, offset=ft.Offset(0,0.2), border_radius=12, width=400, autofocus=True)
        self.text_field_IP = ft.TextField(config[0], label='Server IP',  max_length=100,  offset=ft.Offset(0,0.2), border_radius=12)
        self.text_field_PORT = ft.TextField(config[1], label='Puerto Servidor', max_length=100, offset=ft.Offset(0,0.2), border_radius=12)
        self.container_serie = ft.Container(ft.Text('Series Disponibles') ,offset=ft.Offset(0,0.2), border_radius=12)
        self.dropdown_series = ft.Dropdown(config[3].upper(), options=[
            ft.dropdown.Option(x) for x in config[4]
        ], border_radius=12)
        self.btn_save_data = ft.IconButton(ft.icons.SAVE_ALT_ROUNDED, icon_color=ft.colors.BLUE_400, icon_size=50, tooltip='Guardar Cambios', on_click=self.click_save_data)
        #self.page.floating_action_button = ft.ElevatedButton("Guardar", icon=ft.icons.SAVE, visible=False, on_click=self.click_save_data)
        
        self.column =  ft.Column([self.text_field_ruta_local, self.text_field_IP, self.text_field_PORT, self.container_serie,self.dropdown_series, self.btn_save_data], expand=True)
        self.visible = True
        self.content = self.column
        self.bgcolor = '#474b4e'
        self.border_radius = 12
        self.expand = True

    
    
    def result_data_save(self):
        result_change = saveInitConfig(server_ip=self.text_field_IP.value, port=self.text_field_PORT.value, 
                                       serie=self.dropdown_series.value, ruta_local=self.text_field_ruta_local.value)
        
        if result_change == True:
            return True
        else:
            return result_change 

    def click_save_data(self, e: ft.ControlEvent):
        ip_regex = r'^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$'
        self.message_error_type_data_field = ft.SnackBar(ft.Text(), visible=True, duration=4000, bgcolor=ft.colors.RED_300)

        if not os.path.exists(self.text_field_ruta_local.value + '\sempresas.dat') and self.text_field_ruta_local.label == 'Ruta a2Cash Local':
                self.message_error_type_data_field.content = ft.Text('El directorio especificado no existe o no se encuentra el archivo {Sempresas.dat}')
                self.message_error_type_data_field.open = True
                self.page.overlay.append(self.message_error_type_data_field)
                self.text_field_ruta_local.focused_border_color = ft.colors.RED_300
                self.text_field_ruta_local.focus()
                self.page.update()

        elif not re.match(ip_regex, self.text_field_IP.value ) and self.text_field_IP.label == 'Server IP':
            self.text_field_IP.value = ''
            self.message_error_type_data_field.content = ft.Text('Direccion ip no valida')
            self.message_error_type_data_field.open = True
            self.page.overlay.append(self.message_error_type_data_field)
            self.text_field_IP.focused_border_color = ft.colors.RED_300
            self.text_field_IP.focus()
            self.page.update()
        
        elif not self.text_field_PORT.value.isdigit() or int(self.text_field_PORT.value) > 65535:
                self.message_error_type_data_field.content = ft.Text('El rango de puertos permitidos es de [1:65535]')
                self.message_error_type_data_field.open = True
                self.text_field_PORT.focused_border_color = ft.colors.RED_300
                self.text_field_PORT.focus()
                self.page.overlay.append(self.message_error_type_data_field)
                self.page.update()         
        else:
            result = self.result_data_save()
            if result == True:
                self.message_save_data = ft.SnackBar(ft.Text('Cambios guardados con éxito!') ,action='Alright!', visible=True, duration=4000, bgcolor=ft.colors.GREEN_300)
            else:
                self.message_save_data = ft.SnackBar(ft.Text('Error al intentar guardar los cambios, verifique que el archivo .ini exista'), visible=True, duration=5000, bgcolor=ft.colors.RED_300)    
            self.message_save_data.open = True
            self.page.overlay.append(self.message_save_data)
            self.page.update()





            
