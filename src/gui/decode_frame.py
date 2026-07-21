import customtkinter as ctk
from customtkinter import filedialog
from ..core.encoder import decode, EncodingLevel
from ..utils import utils
from .image_preview import ImagePreview


class DecodeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.lbl_level = ctk.CTkLabel(self, text="Livello di decodifica:")
        self.lbl_level.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        self.level_var = ctk.StringVar(value="LOW")
        self.level_menu = ctk.CTkOptionMenu(
            self,
            values=[lvl.name for lvl in EncodingLevel],
            variable=self.level_var,
        )
        self.level_menu.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # Variabili di stato
        self.stego_img = None
        self.extracted_kind = None
        self.extracted_text = None
        self.extracted_img = None

        self._setup_ui()

        self.bind("<Configure>", self._on_resize)

    def _setup_ui(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Riga 0: Selettore file
        frame_top = ctk.CTkFrame(self, fg_color="transparent")
        frame_top.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        btn_stego = ctk.CTkButton(
            frame_top, text="Scegli Immagine Steganografata", command=self._on_stego_selected
        )
        btn_stego.pack(side="left", padx=(0, 10), pady=10)

        self.lbl_stego_path = ctk.CTkLabel(frame_top, text="Nessun file selezionato")
        self.lbl_stego_path.pack(side="left", padx=10, pady=10)

        # Riga 1: Anteprima stego + area risultato
        frame_mid = ctk.CTkFrame(self, fg_color="transparent")
        frame_mid.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        frame_mid.grid_columnconfigure(0, weight=1)
        frame_mid.grid_columnconfigure(1, weight=1)
        frame_mid.grid_rowconfigure(0, weight=1)

        self.preview_stego = ImagePreview(frame_mid, "Immagine Steganografata")
        self.preview_stego.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Container per il risultato (testo o immagine)
        frame_result = ctk.CTkFrame(frame_mid, fg_color="transparent")
        frame_result.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        frame_result.grid_rowconfigure(0, weight=1)
        frame_result.grid_columnconfigure(0, weight=1)

        self.textbox_result = ctk.CTkTextbox(frame_result)
        self.textbox_result.grid(row=0, column=0, sticky="nsew")
        self.textbox_result.insert("0.0", "Il risultato dell'estrazione apparirà qui...")
        self.textbox_result.configure(state="disabled")

        self.preview_result = ImagePreview(frame_result, "Segreto Estratto")
        self.preview_result.grid(row=0, column=0, sticky="nsew")

        # Riga 2: Bottoni azione e status
        frame_bot = ctk.CTkFrame(self, fg_color="transparent")
        frame_bot.grid(row=4, column=0, sticky="ew", padx=20, pady=10)

        btn_decode = ctk.CTkButton(frame_bot, text="Estrai", command=self._extract)
        btn_decode.pack(side="left", padx=(0, 10))

        self.btn_save = ctk.CTkButton(
            frame_bot, text="Salva Segreto...", command=self._save, state="disabled"
        )
        self.btn_save.pack(side="left", padx=10)

        self.lbl_status = ctk.CTkLabel(
            frame_bot, text="", font=ctk.CTkFont(weight="bold"), anchor="w", justify="left"
        )
        self.lbl_status.pack(side="left", fill="x", expand=True, padx=20)

        # Inizio: mostra textbox, nasconde preview risultato
        self.preview_result.grid_remove()
        self._result_showing_text = True

    def _on_resize(self, event):
        w = self.lbl_status.winfo_width()
        if w > 0:
            self.lbl_status.configure(wraplength=w)

    def _selected_level(self):
        return EncodingLevel[self.level_var.get()]

    def _on_stego_selected(self):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine Steganografata",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")],
        )
        if filename:
            self.lbl_stego_path.configure(text=filename)
            self.stego_img = utils.load(filename)
            self.preview_stego.show(self.stego_img)
            self._reset()

    def _reset(self):
        self.extracted_kind = None
        self.extracted_text = None
        self.extracted_img = None
        self.btn_save.configure(state="disabled")
        self.lbl_status.configure(text="")
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        self.textbox_result.insert("0.0", "Premi 'Estrai' per decodificare.")
        self.textbox_result.configure(state="disabled")
        if not self._result_showing_text:
            self.textbox_result.grid()
            self.preview_result.grid_remove()
            self._result_showing_text = True
        self.preview_result.clear()

    def _show_result_text(self, text):
        if not self._result_showing_text:
            self.textbox_result.grid()
            self.preview_result.grid_remove()
            self._result_showing_text = True
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        self.textbox_result.insert("0.0", text)
        self.textbox_result.configure(state="disabled")

    def _show_result_image(self, img):
        if self._result_showing_text:
            self.textbox_result.grid_remove()
            self.preview_result.grid()
            self._result_showing_text = False
        self.preview_result.show(img)

    def _extract(self):
        if getattr(self, "stego_img", None) is None:
            self.lbl_status.configure(
                text="Seleziona un'immagine steganografata.", text_color="red"
            )
            return

        try:
            kind, data = decode(self.stego_img, self._selected_level())
        except ValueError as e:
            self.lbl_status.configure(text=f"Errore: {e}", text_color="red")
            return

        if kind == "text":
            self.extracted_kind = "text"
            self.extracted_text = data
            self.extracted_img = None
            self._show_result_text(data)
            self.btn_save.configure(state="disabled")
            self.lbl_status.configure(
                text="Testo estratto con successo.", text_color="green"
            )
        else:
            self.extracted_kind = "image"
            self.extracted_text = None
            self.extracted_img = data
            self._show_result_image(data)
            self.btn_save.configure(state="normal")
            self.lbl_status.configure(
                text="Immagine estratta con successo.", text_color="green"
            )

    def _save(self):
        if self.extracted_img is None:
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            title="Salva Immagine Estratta",
            filetypes=[("PNG Image", "*.png")],
        )
        if save_path:
            try:
                self.extracted_img.save(utils.png_path(save_path), "PNG")
                self.lbl_status.configure(
                    text=f"Salvato in: {save_path}", text_color="green"
                )
            except (OSError, ValueError) as e:
                self.lbl_status.configure(
                    text=f"Errore durante il salvataggio: {e}", text_color="red"
                )
