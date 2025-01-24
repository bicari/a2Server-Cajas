import flet as ft
import re
import os
from functions import saveInitConfig
from querys.update_tablas import sqlQuerys
class ConfigPage(ft.ListView):
    def __init__(self, page: ft.Page, config, btn_save_data: ft.FloatingActionButton):
        super().__init__()
        self.init_config = config # [0]IP [1]PORT [2]rutalocal [3]SERIEACTUAL [4]SERIES [5]ruta a2
        self.page = page
        self.text_field_ruta_local = ft.TextField(config[2], label='Ruta a2Cash Local', max_length=100, offset=ft.Offset(0,0.2), border_radius=12,  autofocus=True)
        self.text_field_ruta_a2data = ft.TextField(config[5], label='Ruta a2Data', max_length=100, offset=ft.Offset(0,0.2), border_radius=12,  autofocus=True)
        self.text_field_ruta_a2_cash = ft.TextField(config[6], label='Ruta a2Cash', max_length=100, offset=ft.Offset(0,0.2), border_radius=12,  autofocus=True)
        self.text_field_IP = ft.TextField(config[0], label='Server IP socket',  max_length=100,  offset=ft.Offset(0,0.2), border_radius=12)
        self.text_field_IP_Server_files = ft.TextField(config[8], label='Ip servidor Archivos',  max_length=100,  offset=ft.Offset(0,0.2), border_radius=12)
        self.text_field_PORT = ft.TextField(config[1], label='Puerto Servidor', max_length=100, offset=ft.Offset(0,0.2), border_radius=12)
        self.text_field_PORT_file = ft.TextField(config[9], label='Puerto Servidor Archivos', max_length=100, offset=ft.Offset(0,0.2), border_radius=12)
        self.container_serie = ft.Container(ft.Text('Series Disponibles') ,offset=ft.Offset(0,0.2), border_radius=12)
        self.dropdown_series = ft.Dropdown(config[3].upper(), options=[
            ft.dropdown.Option(x) for x in config[4]
        ], border_radius=12)
        self.desconnection_mode = ft.Switch(label="Desconexión automatica", value=[10])
        self.btn_save_data = ft.IconButton(ft.icons.SAVE_ROUNDED, icon_color=ft.colors.BLUE_400, icon_size=50, tooltip='Guardar Cambios', on_click=self.click_save_data)
        self.desconection_button = ft.IconButton(ft.icons.ERROR_OUTLINE, icon_color=ft.colors.RED_400, icon_size=50,tooltip='Activar contingencia', on_click=self.activar_contingencia)
        self.btn_restaurar_sempresas = ft.IconButton(ft.icons.SYNC_LOCK, icon_color=ft.colors.GREEN_400,icon_size=50, tooltip="Desactivar Contingencia",on_click=self.desactivar_contingencia, disabled=True)
        self.column =  ft.Column([self.text_field_ruta_local, self.text_field_ruta_a2data, self.text_field_ruta_a2_cash, self.text_field_IP, self.text_field_PORT, self.text_field_IP_Server_files, self.text_field_PORT_file, 
                                  self.container_serie,self.dropdown_series, 
                                  self.desconnection_mode,
                                  ft.Row([self.btn_save_data, self.desconection_button,self.btn_restaurar_sempresas ]) ], expand=True)
        self.modal_desconexion = ft.AlertDialog(modal=True, title=ft.Text("Por favor confirme"), content=ft.Text('Desea activar contingencia?'), actions=[ft.ElevatedButton('Sí', on_click=self.modal_yes_click
                                                                                                                                                                    ), ft.OutlinedButton('No', on_click=self.modal_no_click)],
                                                                                                                                                                    actions_alignment=ft.MainAxisAlignment.END)
        self.message_snack_bar = ft.SnackBar(content=ft.Text(), bgcolor=ft.colors.GREEN_300, duration=4000)
        self.visible = True
        self.controls = [ft.Container(content=self.column, bgcolor="#474b4e", expand= True, border_radius=12)]
        self.expand = True

    def desactivar_contingencia(self, e):
        self.modal_desconexion.open = True
        self.modal_desconexion.content = ft.Text("¿Desea desactivar el modo contingencia?")
        self.modal_desconexion.actions = [ft.ElevatedButton('Sí', on_click=self.modal_yes_click, data=0), ft.OutlinedButton('No', on_click=self.modal_no_click)]
        self.page.open(self.modal_desconexion)
        self.page.update()
        

    def modal_yes_click(self, e):
        if e.control.data == 0:
            result = sqlQuerys('DSN=A2GKC; CatalogName={catalogname}'.format(catalogname=self.init_config[6])).update_sempresas_a2cash(path_data_local=self.init_config[5], path_local_formatos_config= os.path.dirname(self.init_config[5]))
            if result:
                self.message_snack_bar.content = ft.Text("Tablas locales actualizadas, contingencia desactivada")
                self.message_snack_bar.open = True
                self.page.overlay.append(self.message_snack_bar)
                self.modal_desconexion.open = False
                self.desconection_button.disabled = False
                self.page.update()
            else:
                self.message_snack_bar.content = ft.Text(result)
                self.message_snack_bar.open = True
                self.page.overlay.append(self.message_snack_bar)
                self.page.update()
        if e.control.data ==  1:
            result = sqlQuerys('DSN=A2GKC; CatalogName={catalogname}'.format(catalogname=self.init_config[6])).update_sempresas_a2cash(path_data_local=self.init_config[2], path_local_formatos_config= os.path.dirname(self.init_config[2]))
            if result:
                self.message_snack_bar.content = ft.Text("Tablas locales actualizadas, contingencia activada")
                self.message_snack_bar.open = True
                self.page.overlay.append(self.message_snack_bar)
                self.modal_desconexion.open = False
                self.desconection_button.disabled = True
                self.desconection_button.icon_color = ft.colors.GREY_100
                self.btn_restaurar_sempresas.disabled = False
                self.page.update()

    def modal_no_click(self, e):
        self.modal_desconexion.open = False
        self.page.update()
        

    def activar_contingencia(self, e: ft.ControlEvent):
        self.modal_desconexion.open = True
        self.modal_desconexion.content = ft.Text("¿Esta seguro de activar el modo fuera de linea?")
        self.modal_desconexion.actions = [ft.ElevatedButton('Sí', on_click=self.modal_yes_click, data=1), ft.OutlinedButton('No', on_click=self.modal_no_click)]
        self.page.open(self.modal_desconexion)
        self.page.update()

        

    
    def result_data_save(self):
        result_change = saveInitConfig(server_ip=self.text_field_IP.value, port=self.text_field_PORT.value, 
                                       serie=self.dropdown_series.value, ruta_local=self.text_field_ruta_local.value, ruta_a2=self.text_field_ruta_a2data.value, 
                                       ruta_a2_cash=self.text_field_ruta_a2_cash.value, portfiles=self.text_field_PORT_file.value, ipfiles=self.text_field_IP_Server_files.value,
                                       connection_mode=str(int(self.desconnection_mode.value)))
        
        if result_change == True:
            return True
        else:
            return result_change 

    def click_save_data(self, e: ft.ControlEvent):
        ip_regex = r'^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$'
        self.message_error_type_data_field = ft.SnackBar(ft.Text(), visible=True, duration=4000, bgcolor=ft.colors.RED_300)
        if not os.path.exists(os.path.dirname(self.text_field_ruta_local.value)  + '\\sempresas.dat') and self.text_field_ruta_local.label == 'Ruta a2Cash Local':
            self.message_error_type_data_field.content = ft.Text('El directorio especificado no existe o no se encuentra el archivo {Sempresas.dat}')
            self.message_error_type_data_field.open = True
            self.page.overlay.append(self.message_error_type_data_field)
            self.text_field_ruta_local.focused_border_color = ft.colors.RED_300
            self.text_field_ruta_local.focus()
            self.page.update()

        elif not os.path.exists(self.text_field_ruta_a2data.value + '\\Sinventario.dat') and self.text_field_ruta_a2data.label == 'Ruta a2Data':
            self.message_error_type_data_field.content = ft.Text('El directorio especificado no contiene la base de datos del sistema a2Hac')
            self.message_error_type_data_field.open = True
            self.page.overlay.append(self.message_error_type_data_field)
            self.text_field_ruta_a2data.focused_bgcolor = ft.colors.RED_300
            self.text_field_ruta_a2data.focus()
            self.page.update()

        elif not os.path.exists(self.text_field_ruta_a2_cash.value + '\\a2Cash.exe') and self.text_field_ruta_a2_cash.label == 'Ruta a2Cash':
            self.message_error_type_data_field.content = ft.Text('El directorio espeficado no contiene el archivo a2Cash.exe')
            self.message_error_type_data_field.open = True
            self.page.overlay.append(self.message_error_type_data_field)
            self.text_field_ruta_a2_cash.focused_bgcolor = ft.colors.RED_300
            self.text_field_ruta_a2_cash.focus()
            self.page.update()    

        elif not re.match(ip_regex, self.text_field_IP.value ) and self.text_field_IP.label == 'Server IP socket':
            self.text_field_IP.value = ''
            self.message_error_type_data_field.content = ft.Text('Direccion ip no valida')
            self.message_error_type_data_field.open = True
            self.page.overlay.append(self.message_error_type_data_field)
            self.text_field_IP.focused_border_color = ft.colors.RED_300
            self.text_field_IP.focus()
            self.page.update()

        elif not re.match(ip_regex, self.text_field_IP_Server_files.value ) and self.text_field_IP_Server_files.label == 'Ip servidor Archivos':
            self.text_field_IP_Server_files.value = ''
            self.message_error_type_data_field.content = ft.Text('Direccion ip no valida')
            self.message_error_type_data_field.open = True
            self.page.overlay.append(self.message_error_type_data_field)
            self.text_field_IP_Server_files.focused_border_color = ft.colors.RED_300
            self.text_field_IP_Server_files.focus()
            self.page.update()    
        
        elif not self.text_field_PORT.value.isdigit() or int(self.text_field_PORT.value) > 65535 or self.text_field_PORT.value == self.text_field_PORT_file.value:
                self.message_error_type_data_field.content = ft.Text('El puerto especificado no esta disponible o está siendo usado')
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
                print(result)
                self.message_save_data = ft.SnackBar(ft.Text('Error al intentar guardar los cambios, verifique que el archivo .ini exista'), visible=True, duration=5000, bgcolor=ft.colors.RED_300)    
            self.message_save_data.open = True
            self.page.overlay.append(self.message_save_data)
            self.page.update()





            
