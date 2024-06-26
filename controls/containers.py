import flet as ft

class ContainersIconsNav(ft.Container):
    def __init__(self, icon: ft.Icon, datos,  page, offset : ft.Offset =  None, hover_click :  bool = True, content_to_show: ft.Container = None, conten_to_close: ft.Container = None):
        super().__init__(icon, data=datos)
        self.content= icon  
        self.width  = 50
        self.height = 50
        self.border_radius = 10
        self.data = datos
        if hover_click:
            self.on_hover = self.hover_color
            self.on_click = self.on_click_icon
        self.offset = offset
        self.content_to_show = content_to_show
        self.content_to_close = conten_to_close
        

    def hover_color(self, e):
        if e.data == 'true':
            e.control.bgcolor = 'black'
            e.control.color = 'white'
            e.control.update()
        else:
            e.control.bgcolor = ft.colors.CYAN_800
            e.control.color = 'black'    
            e.control.update()
               

    def on_click_icon(self,e: ft.ControlEvent):
          if self.data != 'None' and self.content_to_show != None:
              self.content_to_show.visible = True
              self.content_to_close.visible = False
              self.page.update()
 

class GrupoContenedores:
    def __init__(self, page: ft.Page, badge: ft.Badge, page_container_to_show_settings: ft.Container = None, page_container_to_show_sync: ft.Container = None):
        self.page = page
        #self.content_to_show = content_to_show
        self.badge = badge
        self.control_group=[
                ContainersIconsNav(ft.Icon(ft.icons.SETTINGS), datos='0',  page=page, content_to_show=page_container_to_show_settings, conten_to_close=page_container_to_show_sync),
                ContainersIconsNav(ft.Icon(ft.icons.SYNC), datos='1',  page=page, content_to_show=page_container_to_show_sync, conten_to_close=page_container_to_show_settings),
                ContainersIconsNav(self.badge, datos='2', page=page, offset=ft.Offset(x=0.2, y=9.5), hover_click=False)
        ]
    