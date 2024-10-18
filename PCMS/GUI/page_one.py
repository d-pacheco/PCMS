import customtkinter as ctk

class PageOne(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Page One", font=("Helvetica", 24))
        label.pack(pady=20)

        button = ctk.CTkButton(self, text="Back to Home",
                                command=lambda: controller.show_frame("HomePage"))
        button.pack(pady=10)