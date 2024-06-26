import flet as ft


class SyncPage(ft.Container):
    def __init__(self ):
        super().__init__()
        self.content = ft.Column([], expand=True)
        self.expand = True
        self.border_radius = 10
        self.bgcolor = ft.colors.CYAN_800
        self.visible = False