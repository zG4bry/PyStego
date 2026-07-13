import customtkinter as ctk
from customtkinter import filedialog

class DecodeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.tabview.add("Estrai Testo")
        self.tabview.add("Estrai Immagine")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._setup_text_tab()
        self._setup_image_tab()

    def _setup_text_tab(self):
        tab = self.tabview.tab("Estrai Testo")
        tab.grid_columnconfigure(0, weight=1)
        
        self.lbl_stego_text = ctk.CTkLabel(tab, text="Nessun file steganografato selezionato")
        self.lbl_stego_text.grid(row=0, column=0, pady=(10, 0), padx=20)
        
        btn_select_stego = ctk.CTkButton(tab, text="Scegli Immagine Steganografata", command=self.select_stego_text)
        btn_select_stego.grid(row=1, column=0, pady=10, padx=20)
        
        btn_decode = ctk.CTkButton(tab, text="Estrai Testo", command=self.decode_text)
        btn_decode.grid(row=2, column=0, pady=10, padx=20)
        
        self.textbox_result = ctk.CTkTextbox(tab, height=150)
        self.textbox_result.grid(row=3, column=0, pady=10, padx=20, sticky="ew")
        self.textbox_result.insert("0.0", "Il testo estratto apparirà qui...")
        self.textbox_result.configure(state="disabled")

    def _setup_image_tab(self):
        tab = self.tabview.tab("Estrai Immagine")
        tab.grid_columnconfigure(0, weight=1)
        
        self.lbl_stego_img = ctk.CTkLabel(tab, text="Nessun file steganografato selezionato")
        self.lbl_stego_img.grid(row=0, column=0, pady=(10, 0), padx=20)
        
        btn_select_stego = ctk.CTkButton(tab, text="Scegli Immagine Steganografata", command=self.select_stego_img)
        btn_select_stego.grid(row=1, column=0, pady=10, padx=20)
        
        btn_decode = ctk.CTkButton(tab, text="Estrai e Salva Immagine", command=self.decode_image)
        btn_decode.grid(row=2, column=0, pady=10, padx=20)
        
        self.lbl_status_img = ctk.CTkLabel(tab, text="", text_color="green", font=ctk.CTkFont(weight="bold"))
        self.lbl_status_img.grid(row=3, column=0, pady=(10, 20), padx=20)

    def select_stego_text(self):
        filename = filedialog.askopenfilename(title="Seleziona Immagine Steganografata", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.lbl_stego_text.configure(text=f"Immagine: {filename}")

    def select_stego_img(self):
        filename = filedialog.askopenfilename(title="Seleziona Immagine Steganografata", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.lbl_stego_img.configure(text=f"Immagine: {filename}")

    def decode_text(self):
        # TODO: Implement the decoding logic here
        print("Decoding text...")
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        self.textbox_result.insert("0.0", "Testo segreto estratto con successo! (Simulato)")
        self.textbox_result.configure(state="disabled")

    def decode_image(self):
        # TODO: Implement the decoding logic here
        save_path = filedialog.asksaveasfilename(defaultextension=".png", title="Salva Immagine Estratta", filetypes=[("PNG Image", "*.png")])
        if save_path:
            print("Decoding image and saving to:", save_path)
            self.lbl_status_img.configure(text=f"Salvato in: {save_path}")
