import customtkinter as ctk
from customtkinter import filedialog
from ..core.encoder import encode, EncodingLevel
from ..core import metrics
from ..utils import utils
from .image_preview import ImagePreview


class EncodeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)

        self.tabview = ctk.CTkTabview(self, command=self._on_tab_change)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.tabview.add("Nascondi Testo")
        self.tabview.add("Nascondi Immagine")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.lbl_level = ctk.CTkLabel(self, text="Livello di codifica:")
        self.lbl_level.grid(row=1, column=0, padx=20, pady=(0, 0), sticky="w")
        self.level_var = ctk.StringVar(value="LOW")
        self.level_menu = ctk.CTkOptionMenu(
            self,
            values=[lvl.name for lvl in EncodingLevel],
            variable=self.level_var,
        )
        self.level_menu.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        # Variabili di stato condivise
        self.cover_text = None
        self.cover_img = None
        self.secret_img = None
        
        # Per poter salvare dopo aver codificato
        self.encoded_flat_text = None
        self.encoded_flat_img = None

        self._setup_text_tab()
        self._setup_image_tab()

        self.bind("<Configure>", self._on_resize)

    def _on_tab_change(self):
        # Azzeramento tab Testo
        self.cover_text = None
        self.lbl_cover_path_text.configure(text="Nessun file selezionato")
        self.textbox_secret.delete("0.0", "end")
        self.textbox_secret.insert("0.0", self.placeholder_text)
        self.textbox_secret.configure(text_color="gray")
        self.preview_orig_text.clear()
        self.preview_result_text.clear()
        self.encoded_flat_text = None
        self.btn_save_text.configure(state="disabled")
        self.lbl_esito_text.configure(text="")

        # Azzeramento tab Immagine
        self.cover_img = None
        self.secret_img = None
        self.lbl_cover_path_img.configure(text="Nessuna copertura")
        self.lbl_secret_path_img.configure(text="Nessun segreto")
        self.preview_orig_img.clear()
        self.preview_result_img.clear()
        self.encoded_flat_img = None
        self.btn_save_img.configure(state="disabled")
        self.lbl_esito_img.configure(text="")

    def _on_resize(self, event):
        width = self.winfo_width() - 40
        for lbl in (self.lbl_esito_text, self.lbl_esito_img):
            if width > 0:
                lbl.configure(wraplength=width)

    def _selected_level(self):
        return EncodingLevel[self.level_var.get()]

    # --- TAB TESTO ---
    def _setup_text_tab(self):
        tab = self.tabview.tab("Nascondi Testo")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        # Riga 0: Selezione Cover
        frame_top = ctk.CTkFrame(tab, fg_color="transparent")
        frame_top.grid(row=0, column=0, sticky="ew")
        
        btn_cover = ctk.CTkButton(frame_top, text="Scegli Immagine di Copertura", command=self._on_cover_selected_text)
        btn_cover.pack(side="left", padx=(20, 10), pady=10)
        
        self.lbl_cover_path_text = ctk.CTkLabel(frame_top, text="Nessun file selezionato")
        self.lbl_cover_path_text.pack(side="left", padx=10, pady=10)

        # Riga 1: Textbox Segreto
        self.placeholder_text = "Inserisci qui il testo da nascondere..."
        self.textbox_secret = ctk.CTkTextbox(tab, height=100)
        self.textbox_secret.grid(row=1, column=0, pady=10, padx=20, sticky="ew")
        
        self._default_text_color = self.textbox_secret.cget("text_color")
        self.textbox_secret.insert("0.0", self.placeholder_text)
        self.textbox_secret.configure(text_color="gray")
        self.textbox_secret.bind("<FocusIn>", self._clear_placeholder)
        self.textbox_secret.bind("<FocusOut>", self._add_placeholder)

        # Riga 2: Anteprime affiancate
        frame_previews = ctk.CTkFrame(tab, fg_color="transparent")
        frame_previews.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        frame_previews.grid_columnconfigure(0, weight=1)
        frame_previews.grid_columnconfigure(1, weight=1)

        self.preview_orig_text = ImagePreview(frame_previews, "Copertura (Originale)")
        self.preview_orig_text.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.preview_result_text = ImagePreview(frame_previews, "Risultato (Stego)")
        self.preview_result_text.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Riga 3: Bottoni Azione e Label Esito
        frame_bot = ctk.CTkFrame(tab, fg_color="transparent")
        frame_bot.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        btn_encode = ctk.CTkButton(frame_bot, text="Codifica (Genera Anteprima)", command=self._encode_text)
        btn_encode.pack(side="left", padx=(0, 10))
        
        self.btn_save_text = ctk.CTkButton(frame_bot, text="Salva Immagine...", command=self._save_text, state="disabled")
        self.btn_save_text.pack(side="left", padx=10)

        self.lbl_esito_text = ctk.CTkLabel(frame_bot, text="", font=ctk.CTkFont(weight="bold"), justify="left")
        self.lbl_esito_text.pack(side="left", padx=20)

    def _clear_placeholder(self, event):
        current_text = self.textbox_secret.get("0.0", "end-1c")
        if current_text == self.placeholder_text:
            self.textbox_secret.delete("0.0", "end")
            self.textbox_secret.configure(text_color=self._default_text_color)

    def _add_placeholder(self, event):
        current_text = self.textbox_secret.get("0.0", "end-1c")
        if not current_text.strip():
            self.textbox_secret.delete("0.0", "end")
            self.textbox_secret.insert("0.0", self.placeholder_text)
            self.textbox_secret.configure(text_color="gray")

    def _on_cover_selected_text(self):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine di Copertura",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")],
        )
        if filename:
            self.lbl_cover_path_text.configure(text=filename)
            self.cover_text = utils.load(filename)
            self.preview_orig_text.show(self.cover_text)
            # Reset UI
            self.preview_result_text.clear()
            self.encoded_flat_text = None
            self.btn_save_text.configure(state="disabled")
            self.lbl_esito_text.configure(text="")

    def _encode_text(self):
        secret_txt = self.textbox_secret.get("0.0", "end-1c")
        if secret_txt == self.placeholder_text or not secret_txt.strip():
            self.lbl_esito_text.configure(text="Inserisci un testo da nascondere", text_color="red")
            return
        if self.cover_text is None:
            self.lbl_esito_text.configure(text="Seleziona prima l'immagine di copertura", text_color="red")
            return
            
        try:
            flat_arr = encode(self.cover_text, secret_txt, self._selected_level())
            self.encoded_flat_text = flat_arr
            
            # Ricostruisce immagine per anteprima e ssim
            width, height = self.cover_text.size
            result_img = utils.flat_to_image(flat_arr, width, height)
            
            self.preview_result_text.show(result_img)
            ssim_val = metrics.ssim(self.cover_text, result_img)
            
            self.lbl_esito_text.configure(text=f"Codifica riuscita. SSIM: {ssim_val:.5f}", text_color="green")
            self.btn_save_text.configure(state="normal")
            
        except ValueError as e:
            self.lbl_esito_text.configure(text=f"Errore: {e}", text_color="red")

    def _save_text(self):
        if self.encoded_flat_text is None:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="Salva Immagine Codificata",
            filetypes=[("PNG Image", "*.png")],
        )
        if save_path:
            try:
                width, height = self.cover_text.size
                utils.save(self.encoded_flat_text, width, height, save_path, "png")
                self.lbl_esito_text.configure(text=f"Salvato in: {save_path}", text_color="green")
            except ValueError as e:
                self.lbl_esito_text.configure(text=f"Errore durante il salvataggio: {e}", text_color="red")

    # --- TAB IMMAGINE ---
    def _setup_image_tab(self):
        tab = self.tabview.tab("Nascondi Immagine")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Riga 0: Selettori
        frame_top = ctk.CTkFrame(tab, fg_color="transparent")
        frame_top.grid(row=0, column=0, sticky="ew")
        
        btn_cover = ctk.CTkButton(frame_top, text="Scegli Copertura", command=self._on_cover_selected_img)
        btn_cover.grid(row=0, column=0, padx=20, pady=10)
        self.lbl_cover_path_img = ctk.CTkLabel(frame_top, text="Nessuna copertura")
        self.lbl_cover_path_img.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        btn_secret = ctk.CTkButton(frame_top, text="Scegli Immagine da Nascondere", command=self._on_secret_selected_img)
        btn_secret.grid(row=1, column=0, padx=20, pady=10)
        self.lbl_secret_path_img = ctk.CTkLabel(frame_top, text="Nessun segreto")
        self.lbl_secret_path_img.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Riga 1: Anteprime affiancate (Copertura vs Risultato)
        frame_previews = ctk.CTkFrame(tab, fg_color="transparent")
        frame_previews.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        frame_previews.grid_columnconfigure(0, weight=1)
        frame_previews.grid_columnconfigure(1, weight=1)

        self.preview_orig_img = ImagePreview(frame_previews, "Copertura (Originale)")
        self.preview_orig_img.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.preview_result_img = ImagePreview(frame_previews, "Risultato (Stego)")
        self.preview_result_img.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Riga 2: Bottoni Azione e Label Esito
        frame_bot = ctk.CTkFrame(tab, fg_color="transparent")
        frame_bot.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        btn_encode = ctk.CTkButton(frame_bot, text="Codifica (Genera Anteprima)", command=self._encode_image)
        btn_encode.pack(side="left", padx=(0, 10))
        
        self.btn_save_img = ctk.CTkButton(frame_bot, text="Salva Immagine...", command=self._save_image, state="disabled")
        self.btn_save_img.pack(side="left", padx=10)

        self.lbl_esito_img = ctk.CTkLabel(frame_bot, text="", font=ctk.CTkFont(weight="bold"), justify="left")
        self.lbl_esito_img.pack(side="left", padx=20)

    def _on_cover_selected_img(self):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine di Copertura",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")],
        )
        if filename:
            self.lbl_cover_path_img.configure(text=filename)
            self.cover_img = utils.load(filename)
            self.preview_orig_img.show(self.cover_img)
            self._reset_img_tab()

    def _on_secret_selected_img(self):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine da Nascondere",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")],
        )
        if filename:
            self.lbl_secret_path_img.configure(text=filename)
            self.secret_img = utils.load(filename)
            self._reset_img_tab()

    def _reset_img_tab(self):
        self.preview_result_img.clear()
        self.encoded_flat_img = None
        self.btn_save_img.configure(state="disabled")
        self.lbl_esito_img.configure(text="")

    def _encode_image(self):
        if getattr(self, "cover_img", None) is None:
            self.lbl_esito_img.configure(text="Seleziona prima l'immagine di copertura", text_color="red")
            return
        if getattr(self, "secret_img", None) is None:
            self.lbl_esito_img.configure(text="Seleziona l'immagine da nascondere", text_color="red")
            return
            
        try:
            flat_arr = encode(self.cover_img, self.secret_img, self._selected_level())
            self.encoded_flat_img = flat_arr
            
            width, height = self.cover_img.size
            result_img = utils.flat_to_image(flat_arr, width, height)
            
            self.preview_result_img.show(result_img)
            ssim_val = metrics.ssim(self.cover_img, result_img)
            
            self.lbl_esito_img.configure(text=f"Codifica riuscita. SSIM: {ssim_val:.5f}", text_color="green")
            self.btn_save_img.configure(state="normal")
            
        except ValueError as e:
            self.lbl_esito_img.configure(text=f"Errore: {e}", text_color="red")

    def _save_image(self):
        if self.encoded_flat_img is None:
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="Salva Immagine Codificata",
            filetypes=[("PNG Image", "*.png")],
        )
        if save_path:
            try:
                width, height = self.cover_img.size
                utils.save(self.encoded_flat_img, width, height, save_path, "png")
                self.lbl_esito_img.configure(text=f"Salvato in: {save_path}", text_color="green")
            except ValueError as e:
                self.lbl_esito_img.configure(text=f"Errore durante il salvataggio: {e}", text_color="red")
