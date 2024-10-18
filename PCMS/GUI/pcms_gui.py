import customtkinter as ctk

from PCMS.GUI.home_page import HomePage
from PCMS.GUI.data_page import DataEntryPage
from PCMS.GUI.page_one import PageOne

class PcmsGUI(ctk.CTk):
    def __init__(self, jobber_service, invoice_service):
        super().__init__()

        self.title("Pacheco Contracting Management System")
        self.geometry("600x500")

        # Create a container to hold all pages
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Initialize pages
        self.pages = {}
        for Page in (HomePage, DataEntryPage, PageOne):
            page_name = Page.__name__
            if page_name == HomePage.__name__:
                frame = Page(parent=self.container, controller=self, jobber_service=jobber_service, invoice_service=invoice_service)
            else:
                frame = Page(parent=self.container, controller=self)
            self.pages[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)  # Allow the row to expand
        self.container.grid_columnconfigure(0, weight=1)  # Allow the column to expand

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.pages[page_name]
        frame.tkraise()
