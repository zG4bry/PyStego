import customtkinter as ctk
from customtkinter import filedialog
from ..core.encoder import decode, EncodingLevel
from ..utils import utils
from .image_preview import ImagePreview


class DecodeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)

        self.tabview = ctk.CTkTabview(self, command=self._on_tab_change)
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

        # Variabili di stato condivise
        self.stego_text_img = None
        self.stego_img_img = None
        self.extracted_img = None

        self._setup_text_tab()
        self._setup_image_tab()

        self.bind("<Configure>", self._on_resize)

    def _on_tab_change(self):
        # Azzeramento tab Testo
        self.stego_text_img = None
        self.lbl_stego_path_text.configure(text="Nessun file selezionato")
        self.preview_stego_text.clear()
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        self.textbox_result.insert("0.0", "Il testo estratto apparirà qui...")
        self.textbox_result.configure(state="disabled")

        # Azzeramento tab Immagine
        self.stego_img_img = None
        self.lbl_stego_path_img.configure(text="Nessun file selezionato")
        self.preview_stego_img.clear()
        self.preview_result_img.clear()
        self.extracted_img = None
        self.btn_save_img.configure(state="disabled")
        self.lbl_status_img.configure(text="")

    def _on_resize(self, event):
        width = self.winfo_width() - 40
        if width > 0:
            self.lbl_status_img.configure(wraplength=width)

    def _selected_level(self):
        return EncodingLevel[self.level_var.get()]

    # --- TAB TESTO ---
    def _setup_text_tab(self):
        tab = self.tabview.tab("Estrai Testo")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Riga 0: Selettore
        frame_top = ctk.CTkFrame(tab, fg_color="transparent")
        frame_top.grid(row=0, column=0, sticky="ew")

        btn_stego = ctk.CTkButton(frame_top, text="Scegli Immagine Steganografata", command=self._on_stego_selected_text)
        btn_stego.pack(side="left", padx=(20, 10), pady=10)
        
        self.lbl_stego_path_text = ctk.CTkLabel(frame_top, text="Nessun file selezionato")
        self.lbl_stego_path_text.pack(side="left", padx=10, pady=10)

        # Riga 1: Contenuto centrale (Anteprima + Textbox)
        frame_mid = ctk.CTkFrame(tab, fg_color="transparent")
        frame_mid.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        frame_mid.grid_columnconfigure(0, weight=1)
        frame_mid.grid_columnconfigure(1, weight=1)
        frame_mid.grid_rowconfigure(0, weight=1)

        self.preview_stego_text = ImagePreview(frame_mid, "Immagine Steganografata")
        self.preview_stego_text.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.textbox_result = ctk.CTkTextbox(frame_mid)
        self.textbox_result.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.textbox_result.insert("0.0", "Il testo estratto apparirà qui...")
        self.textbox_result.configure(state="disabled")

        # Riga 2: Azione
        frame_bot = ctk.CTkFrame(tab, fg_color="transparent")
        frame_bot.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        btn_decode = ctk.CTkButton(frame_bot, text="Estrai Testo", command=self._decode_text)
        btn_decode.pack(side="left", padx=(0, 20))

    def _on_stego_selected_text(self):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine Steganografata",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filename:
            self.lbl_stego_path_text.configure(text=filename)
            self.stego_text_img = utils.load(filename)
            self.preview_stego_text.show(self.stego_text_img)
            self.textbox_result.configure(state="normal")
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", "Premi 'Estrai Testo' per continuare.")
            self.textbox_result.configure(state="disabled")

    def _decode_text(self):
        if getattr(self, "stego_text_img", None) is None:
            self.textbox_result.configure(state="normal")
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", "Seleziona un'immagine steganografata.")
            self.textbox_result.configure(state="disabled")
            return
            
        try:
            kind, data = decode(self.stego_text_img, self._selected_level())
        except ValueError as e:
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

    # --- TAB IMMAGINE ---
    def _setup_image_tab(self):
        tab = self.tabview.tab("Estrai Immagine")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Riga 0: Selettore
        frame_top = ctk.CTkFrame(tab, fg_color="transparent")
        frame_top.grid(row=0, column=0, sticky="ew")

        btn_stego = ctk.CTkButton(frame_top, text="Scegli Immagine Steganografata", command=self._on_stego_selected_img)
        btn_stego.pack(side="left", padx=(20, 10), pady=10)
        
        self.lbl_stego_path_img = ctk.CTkLabel(frame_top, text="Nessun file selezionato")
        self.lbl_stego_path_img.pack(side="left", padx=10, pady=10)

        # Riga 1: Anteprime affiancate
        frame_previews = ctk.CTkFrame(tab, fg_color="transparent")
        frame_previews.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        frame_previews.grid_columnconfigure(0, weight=1)
        frame_previews.grid_columnconfigure(1, weight=1)

        self.preview_stego_img = ImagePreview(frame_previews, "Immagine Steganografata")
        self.preview_stego_img.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.preview_result_img = ImagePreview(frame_previews, "Segreto Estratto")
        self.preview_result_img.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Riga 2: Azione
        frame_bot = ctk.CTkFrame(tab, fg_color="transparent")
        frame_bot.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        btn_decode = ctk.CTkButton(frame_bot, text="Estrai (Genera Anteprima)", command=self._decode_image)
        btn_decode.pack(side="left", padx=(0, 10))
        
        self.btn_save_img = ctk.CTkButton(frame_bot, text="Salva Segreto...", command=self._save_image, state="disabled")
        self.btn_save_img.pack(side="left", padx=10)

        self.lbl_status_img = ctk.CTkLabel(frame_bot, text="", font=ctk.CTkFont(weight="bold"), anchor="w", justify="left")
        self.lbl_status_img.pack(side="left", padx=20)

    def _on_stego_selected_img(self):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine Steganografata",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filename:
            self.lbl_stego_path_img.configure(text=filename)
            self.stego_img_img = utils.load(filename)
            self.preview_stego_img.show(self.stego_img_img)
            # Reset UI
            self.preview_result_img.clear()
            self.extracted_img = None
            self.btn_save_img.configure(state="disabled")
            self.lbl_status_img.configure(text="")

    def _decode_image(self):
        if getattr(self, "stego_img_img", None) is None:
            self.lbl_status_img.configure(text="Seleziona un'immagine steganografata.", text_color="red")
            return
            
        try:
            kind, data = decode(self.stego_img_img, self._selected_level())
        except ValueError as e:
            self.lbl_status_img.configure(text=f"Errore: {e}", text_color="red")
            return

        if kind != "image":
            self.lbl_status_img.configure(
                text="Il segreto estratto è un testo, usa l'altra scheda.", text_color="red"
            )
            return

        self.extracted_img = data
        self.preview_result_img.show(self.extracted_img)
        self.lbl_status_img.configure(text="Estrazione riuscita.", text_color="green")
        self.btn_save_img.configure(state="normal")

    def _save_image(self):
        if self.extracted_img is None:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="Salva Immagine Estratta",
            filetypes=[("PNG Image", "*.png")]
        )
        if save_path:
            try:
                self.extracted_img.save(utils.png_path(save_path), "PNG")
                self.lbl_status_img.configure(text=f"Salvato in: {save_path}", text_color="green")
            except (OSError, ValueError) as e:
                self.lbl_status_img.configure(text=f"Errore durante il salvataggio: {e}", text_color="red")
