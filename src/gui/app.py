import customtkinter as ctk
from .sidebar import Sidebar
from .encode_frame import EncodeFrame
from .decode_frame import DecodeFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PyStego")
        self.geometry("1000x740")
        self.minsize(800, 600)

        # Layout principale
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Frame contenitore per le viste
        self.frames = {}
        
        self.frames["encode"] = EncodeFrame(self)
        self.frames["decode"] = DecodeFrame(self)

        # Inizialmente mostra la schermata di codifica
        self.show_frame("encode")

    def show_frame(self, name):
        # Nascondi tutti i frame
        for frame in self.frames.values():
            frame.grid_forget()
            
        # Mostra il frame richiesto
        frame = self.frames[name]
        frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
