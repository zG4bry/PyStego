import customtkinter as ctk
from customtkinter import filedialog

class EncodeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.tabview.add("Nascondi Testo")
        self.tabview.add("Nascondi Immagine")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._setup_text_tab()
        self._setup_image_tab()

    def _setup_text_tab(self):
        tab = self.tabview.tab("Nascondi Testo")
        tab.grid_columnconfigure(0, weight=1)
        
        self.lbl_cover_text = self._setup_cover_selector(tab, lambda: self._on_cover_selected(self.lbl_cover_text))
        
        self.placeholder_text = "Inserisci qui il testo da nascondere..."
        self.textbox_secret = ctk.CTkTextbox(tab, height=150)
        self.textbox_secret.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        self._default_text_color = self.textbox_secret.cget("text_color")
        self.textbox_secret.insert("0.0", self.placeholder_text)
        self.textbox_secret.configure(text_color="gray")
        
        self.textbox_secret.bind("<FocusIn>", self._clear_placeholder)
        self.textbox_secret.bind("<FocusOut>", self._add_placeholder)
        
        btn_encode = ctk.CTkButton(tab, text="Codifica e Salva", command=self._encode_text)
        btn_encode.grid(row=3, column=0, pady=10, padx=20)
        
        self.lbl_ssim_text = ctk.CTkLabel(tab, text="SSIM: In attesa...", font=ctk.CTkFont(weight="bold"))
        self.lbl_ssim_text.grid(row=4, column=0, pady=(10, 20), padx=20)

    def _setup_image_tab(self):
        tab = self.tabview.tab("Nascondi Immagine")
        tab.grid_columnconfigure(0, weight=1)
        
        self.lbl_cover_img = self._setup_cover_selector(tab, lambda: self._on_cover_selected(self.lbl_cover_img))
        
        self.lbl_secret_img = self._setup_secret_img_selector(tab, lambda: self._on_secret_img_selected(self.lbl_secret_img))
        
        btn_encode = ctk.CTkButton(tab, text="Codifica e Salva", command=self._encode_image)
        btn_encode.grid(row=4, column=0, pady=10, padx=20)
        
        self.lbl_ssim_img = ctk.CTkLabel(tab, text="SSIM: In attesa...", font=ctk.CTkFont(weight="bold"))
        self.lbl_ssim_img.grid(row=5, column=0, pady=(10, 20), padx=20)

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

    def _setup_cover_selector(self, tab, command):
        lbl = ctk.CTkLabel(tab, text="Nessun file di copertura selezionato")
        lbl.grid(row=0, column=0, pady=(10, 0), padx=20)

        btn = ctk.CTkButton(tab, text="Scegli Immagine di Copertura", command=command)
        btn.grid(row=1, column=0, pady=10, padx=20)

        return lbl
    
    def _on_cover_selected(self, label):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine di Copertura",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filename:
            label.configure(text=f"Copertura: {filename}")

    def _setup_secret_img_selector(self, tab, command):
        lbl = ctk.CTkLabel(tab, text="Nessuna immagine da nascondere selezionata")
        lbl.grid(row=2, column=0, pady=(10, 0), padx=20)
        
        btn = ctk.CTkButton(tab, text="Scegli Immagine da Nascondere", command=command)
        btn.grid(row=3, column=0, pady=10, padx=20)
        
        return lbl
        

    def _on_secret_img_selected(self, label):
        filename = filedialog.askopenfilename(
            title="Seleziona Immagine da Nascondere", 
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if filename:
            label.configure(text=f"Segreto: {filename}")

    def _encode_text(self):
        # TODO: Implement the encoding logic here
        save_path = filedialog.asksaveasfilename(defaultextension=".png", title="Salva Immagine Codificata", filetypes=[("PNG Image", "*.png")])
        if save_path:
            print("Encoding text and saving to:", save_path)
            # Placeholder for SSIM
            self.lbl_ssim_text.configure(text="SSIM: 0.99 (Simulato)")

    def _encode_image(self):
        # TODO: Implement the encoding logic here
        save_path = filedialog.asksaveasfilename(defaultextension=".png", title="Salva Immagine Codificata", filetypes=[("PNG Image", "*.png")])
        if save_path:
            print("Encoding image and saving to:", save_path)
            # Placeholder for SSIM
            self.lbl_ssim_img.configure(text="SSIM: 0.98 (Simulato)")
