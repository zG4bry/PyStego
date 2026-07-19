import customtkinter as ctk
from PIL import Image
from ..utils import utils

class ImagePreview(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, corner_radius=5, **kwargs)
        
        self.title_lbl = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(weight="bold"))
        self.title_lbl.pack(pady=(5, 5))
        
        self.img_lbl = ctk.CTkLabel(self, text="Nessuna immagine")
        self.img_lbl.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Manteniamo un riferimento forte alla CTkImage per evitare GC
        self._current_ctk_img = None

    def show(self, pil_image: Image.Image):
        """Mostra l'immagine creandone una miniatura per la GUI."""
        thumb = utils.make_thumbnail(pil_image, max_side=260)
        self._current_ctk_img = ctk.CTkImage(light_image=thumb, dark_image=thumb, size=thumb.size)
        self.img_lbl.configure(image=self._current_ctk_img, text="")

    def clear(self):
        """Svuota l'anteprima."""
        self._current_ctk_img = None
        self.img_lbl.configure(image="", text="Nessuna immagine")
