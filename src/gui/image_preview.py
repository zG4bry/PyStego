import customtkinter as ctk
from PIL import Image


class ImagePreview(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(weight="bold"), anchor="center"
        )
        self.title_lbl.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.img_lbl = ctk.CTkLabel(self, text="Nessuna immagine", anchor="center")
        self.img_lbl.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")

        self._original_img = None
        self._ctk_img = None

    def show(self, pil_image: Image.Image):
        if pil_image is None:
            return

        self._original_img = pil_image
        self._resize()
        self.after(50, self._resize)

    def clear(self):
        self._original_img = None
        self._ctk_img = None
        self.img_lbl.configure(image="", text="Nessuna immagine")

    def _resize(self):
        if self._original_img is None:
            return
        w_box = self.winfo_width() - 40
        h_box = self.winfo_height() - 70
        if w_box <= 20 or h_box <= 20:
            return
        orig_w, orig_h = self._original_img.size
        ratio = min(w_box / orig_w, h_box / orig_h, 1.0)
        new_w, new_h = int(orig_w * ratio), int(orig_h * ratio)
        self._ctk_img = ctk.CTkImage(
            light_image=self._original_img,
            dark_image=self._original_img,
            size=(new_w, new_h),
        )
        self.img_lbl.configure(image=self._ctk_img, text="")
