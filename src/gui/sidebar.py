import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.grid_rowconfigure(4, weight=1) 

        self.logo_label = ctk.CTkLabel(self, text="PyStego", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_hide_text = ctk.CTkButton(self, text="Testo in Immagine", command=self.show_text_stego)
        self.btn_hide_text.grid(row=1, column=0, padx=20, pady=10)

        self.btn_hide_image = ctk.CTkButton(self, text="Immagine in Immagine", command=self.show_image_stego)
        self.btn_hide_image.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_ssim = ctk.CTkButton(self, text="Calcola SSIM", command=self.show_ssim_tool)
        self.btn_ssim.grid(row=3, column=0, padx=20, pady=10)

    # 4. Metodi segnaposto (placeholder) per evitare crash
    def show_text_stego(self):
        print("Mostra schermata Testo in Immagine")

    def show_image_stego(self):
        print("Mostra schermata Immagine in Immagine")

    def show_ssim_tool(self):
        print("Mostra schermata Calcola SSIM")