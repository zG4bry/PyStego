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
        
        self.lbl_cover_text = ctk.CTkLabel(tab, text="Nessun file di copertura selezionato")
        self.lbl_cover_text.grid(row=0, column=0, pady=(10, 0), padx=20)
        
        btn_select_cover = ctk.CTkButton(tab, text="Scegli Immagine di Copertura", command=self.select_cover_text)
        btn_select_cover.grid(row=1, column=0, pady=10, padx=20)
        
        self.textbox_secret = ctk.CTkTextbox(tab, height=150)
        self.textbox_secret.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        self.textbox_secret.insert("0.0", "Inserisci qui il testo da nascondere...")
        
        btn_encode = ctk.CTkButton(tab, text="Codifica e Salva", command=self.encode_text)
        btn_encode.grid(row=3, column=0, pady=10, padx=20)
        
        self.lbl_ssim_text = ctk.CTkLabel(tab, text="SSIM: In attesa...", font=ctk.CTkFont(weight="bold"))
        self.lbl_ssim_text.grid(row=4, column=0, pady=(10, 20), padx=20)

    def _setup_image_tab(self):
        tab = self.tabview.tab("Nascondi Immagine")
        tab.grid_columnconfigure(0, weight=1)
        
        self.lbl_cover_img = ctk.CTkLabel(tab, text="Nessun file di copertura selezionato")
        self.lbl_cover_img.grid(row=0, column=0, pady=(10, 0), padx=20)
        
        btn_select_cover = ctk.CTkButton(tab, text="Scegli Immagine di Copertura", command=self.select_cover_img)
        btn_select_cover.grid(row=1, column=0, pady=10, padx=20)
        
        self.lbl_secret_img = ctk.CTkLabel(tab, text="Nessuna immagine da nascondere selezionata")
        self.lbl_secret_img.grid(row=2, column=0, pady=(10, 0), padx=20)
        
        btn_select_secret = ctk.CTkButton(tab, text="Scegli Immagine da Nascondere", command=self.select_secret_img)
        btn_select_secret.grid(row=3, column=0, pady=10, padx=20)
        
        btn_encode = ctk.CTkButton(tab, text="Codifica e Salva", command=self.encode_image)
        btn_encode.grid(row=4, column=0, pady=10, padx=20)
        
        self.lbl_ssim_img = ctk.CTkLabel(tab, text="SSIM: In attesa...", font=ctk.CTkFont(weight="bold"))
        self.lbl_ssim_img.grid(row=5, column=0, pady=(10, 20), padx=20)

    def select_cover_text(self):
        filename = filedialog.askopenfilename(title="Seleziona Immagine", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.lbl_cover_text.configure(text=f"Copertura: {filename}")

    def select_cover_img(self):
        filename = filedialog.askopenfilename(title="Seleziona Immagine di Copertura", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.lbl_cover_img.configure(text=f"Copertura: {filename}")

    def select_secret_img(self):
        filename = filedialog.askopenfilename(title="Seleziona Immagine da Nascondere", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.lbl_secret_img.configure(text=f"Segreto: {filename}")

    def encode_text(self):
        # TODO: Implement the encoding logic here
        save_path = filedialog.asksaveasfilename(defaultextension=".png", title="Salva Immagine Codificata", filetypes=[("PNG Image", "*.png")])
        if save_path:
            print("Encoding text and saving to:", save_path)
            # Placeholder for SSIM
            self.lbl_ssim_text.configure(text="SSIM: 0.99 (Simulato)")

    def encode_image(self):
        # TODO: Implement the encoding logic here
        save_path = filedialog.asksaveasfilename(defaultextension=".png", title="Salva Immagine Codificata", filetypes=[("PNG Image", "*.png")])
        if save_path:
            print("Encoding image and saving to:", save_path)
            # Placeholder for SSIM
            self.lbl_ssim_img.configure(text="SSIM: 0.98 (Simulato)")
