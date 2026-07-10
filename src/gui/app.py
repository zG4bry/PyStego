import customtkinter as ctk
from .sidebar import Sidebar
from .mainframe import MainFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PyStego")
        self.geometry("800x600")

        # Sidebar
        self.sidebar = Sidebar(self).grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)

        # Main Frame
        self.main_frame = MainFrame(self).grid(row=0, column=1, padx = 20, pady = 20, sticky="nsew")
        self.grid_columnconfigure(1, weight=1)
