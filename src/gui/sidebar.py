import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.master = master
        self._next_row = 0

        logo_label = ctk.CTkLabel(
            self, text="PyStego", font=ctk.CTkFont(size=20, weight="bold")
        )
        self._place_widget(logo_label, pady=(20, 10))

        self.btn_encode = self._add_button(
            command=self.show_encode_view,
            text="Codifica (Nascondi)",
        )

        self.btn_decode = self._add_button(
            command=self.show_decode_view,
            text="Decodifica (Estrai)",
        )

        self.grid_rowconfigure(self._next_row, weight=1)

    def _grid_next(self):
        row = self._next_row
        self._next_row += 1
        return row

    def _place_widget(self, widget, column=0, padx=20, pady=10):
        widget.grid(row=self._grid_next(), column=column, padx=padx, pady=pady)
        return widget

    def _add_button(self, command, text, **kwargs):
        button = ctk.CTkButton(self, command=command, text=text, **kwargs)
        return self._place_widget(button)

    def show_encode_view(self):
        self.master.show_frame("encode")

    def show_decode_view(self):
        self.master.show_frame("decode")
