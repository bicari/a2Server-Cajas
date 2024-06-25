import pystray
from PIL import Image
from flet import Page

class Icon(pystray.Icon):
    def __init__(self, icon=None, title=None, menu=None, page: Page = None, **kwargs):
        super().__init__( icon, title, menu, **kwargs)
        self.icon = icon
        self.title = title
        self.menu = pystray.Menu(
         pystray.MenuItem(
             "Open App",
             self.menu_item_clicked,  # alternative/broader callback: menu_item_clicked
             default=True  # set as default menu item
         ),

         pystray.MenuItem(
             "Cambiar Icono",
             self.menu_item_clicked
         )
         )
        self.p = page
        self.run_detached(setup=self.run_icon)

    def run_icon(self, icon):
        icon.visible = False    

        
    def menu_item_clicked(self, icon, query):
        
        if str(query) == "Open App":
            icon.visible = False
            self.p.window.skip_task_bar = False
            self.p.window.maximized = True
            self.p.window.max_height = 720
            self.p.window.max_width = 1280
            self.p.window.height = 600
            self.p.window.width = 800
            self.p.update()
            print("Default button was pressed.")
        if str(query) == "Cambiar Icono":
            print(icon._icon_valid)
            icon.icon = Image.open("flet-controls\\images\\Desconectado.png")  
            

# tray_icon = pystray.Icon(
#     name="Test",
#     icon=icon_minimize,
#     title="Flet in tray",
#     menu=pystray.Menu(
#         pystray.MenuItem(
#             "Open App",
#             menu_item_clicked,  # alternative/broader callback: menu_item_clicked
#             default=True  # set as default menu item
#         ),

#         pystray.MenuItem(
#             "Cambiar Icono",
#             menu_item_clicked
#         )
        

        
#     ),
#     visible=False,
# )