import customtkinter as ctk
from customtkinter import filedialog

from ..core.encoder import decode, EncodingLevel
from ..utils import utils


class DecodeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.tabview.add("Estrai Testo")
        self.tabview.add("Estrai Immagine")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.lbl_level = ctk.CTkLabel(self, text="Livello di decodifica:")
        self.lbl_level.grid(row=1, column=0, padx=20, pady=(0, 0), sticky="w")
        self.level_var = ctk.StringVar(value="LOW")
        self.level_menu = ctk.CTkOptionMenu(
            self,
            values=[lvl.name for lvl in EncodingLevel],
            variable=self.level_var,
        )
        self.level_menu.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        self._setup_text_tab()
        self._setup_image_tab()

    def _selected_level(self):
        return EncodingLevel[self.level_var.get()]

    def _setup_text_tab(self):
        tab = self.tabview.tab("Estrai Testo")
        tab.grid_columnconfigure(0, weight=1)

        self.lbl_stego_text = self._setup_stego_selector(
            tab, lambda: self._on_stego_selected(self.lbl_stego_text)
        )

        btn_decode = ctk.CTkButton(tab, text="Estrai Testo", command=self._decode_text)
        btn_decode.grid(row=2, column=0, pady=10, padx=20)

        self.textbox_result = ctk.CTkTextbox(tab, height=150)
        self.textbox_result.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        self.textbox_result.insert("0.0", "Il testo estratto apparirà qui...")
        self.textbox_result.configure(state="disabled")

    def _setup_image_tab(self):
        tab = self.tabview.tab("Estrai Immagine")
        tab.grid_columnconfigure(0, weight=1)

        self.lbl_stego_img = self._setup_stego_selector(
            tab, lambda: self._on_stego_selected(self.lbl_stego_img)
        )

        btn_decode = ctk.CTkButton(tab, text="Estrai e Salva Immagine", command=self._decode_image)
        btn_decode.grid(row=2, column=0, pady=10, padx=20)

        self.lbl_status_img = ctk.CTkLabel(tab, text="", text_color="green", font=ctk.CTkFont(weight="bold"))
        self.lbl_status_img.grid(row=3, column=0, pady=(10, 20), padx=20)

    def _setup_stego_selector(self, tab, command):
        lbl = ctk.CTkLabel(tab, text="Nessun file steganografato selezionato")
        lbl.grid(row=0, column=0, pady=(10, 0), padx=20)

        btn = ctk.CTkButton(tab, text="Scegli Immagine Steganografata", command=command)
        btn.grid(row=1, column=0, pady=10, padx=20)

        return lbl

    def _on_stego_selected(self, label):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine Steganografata",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filename:
            label.configure(text=f"Immagine: {filename}")
            self.stego_path = filename

    def _decode_text(self):
        if not getattr(self, "stego_path", None):
            self.textbox_result.configure(state="normal")
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", "Seleziona un'immagine steganografata.")
            self.textbox_result.configure(state="disabled")
            return
        try:
            stego = utils.load(self.stego_path)
            kind, data = decode(stego, self._selected_level())
        except (ValueError, Exception) as e:
            self.textbox_result.configure(state="normal")
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", f"Errore: {e}")
            self.textbox_result.configure(state="disabled")
            return

        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        if kind == "text":
            self.textbox_result.insert("0.0", data)
        else:
            self.textbox_result.insert("0.0", "Il segreto estratto è un'immagine, usa l'altra scheda.")
        self.textbox_result.configure(state="disabled")

    def _decode_image(self):
        if not getattr(self, "stego_path", None):
            self.lbl_status_img.configure(text="Seleziona un'immagine steganografata.", text_color="red")
            return
        try:
            stego = utils.load(self.stego_path)
            kind, data = decode(stego, self._selected_level())
        except ValueError as e:
            self.lbl_status_img.configure(text=f"Errore: {e}", text_color="red")
            return

        if kind != "image":
            self.lbl_status_img.configure(
                text="Il segreto estratto è un testo, usa l'altra scheda.", text_color="red"
            )
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="Salva Immagine Estratta",
            filetypes=[("PNG Image", "*.png")]
        )
        if save_path:
            data.save(utils.png_path(save_path), "PNG")
            print("Decoding image and saving to:", save_path)
            self.lbl_status_img.configure(text=f"Salvato in: {save_path}", text_color="green")
