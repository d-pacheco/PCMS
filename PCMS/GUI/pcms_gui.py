import logging
import sys

import customtkinter as ctk
import tkinter.messagebox as messagebox

from PCMS.GUI.home_page import HomePage
from PCMS.GUI.data_page import DataEntryPage
from PCMS.GUI.page_one import PageOne
from PCMS.util.version_manager import VersionManager


logger = logging.getLogger("pcms")


class PcmsGUI(ctk.CTk):
    def __init__(self, jobber_service, invoice_service, version_manager: VersionManager):
        super().__init__()
        self.version_manager = version_manager

        self.title("Pacheco Contracting Management System")
        width = 400
        height = 300
        self.geometry(f"{width}x{height}")

        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

        self.resizable(False, False)

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
        self.check_latest_version()

    def show_frame(self, page_name):
        frame = self.pages[page_name]
        frame.tkraise()

    def check_latest_version(self):
        try:
            if self.version_manager.is_latest_version():
                return

            response = messagebox.askyesno("UPDATE AVAILABLE", "Would you like to download the latest version?")

            if response:
                self.version_manager.download_latest_version()
                messagebox.showinfo("Download Completed!", "Please restart program with new file.")
                sys.exit(0)
        except Exception as e:
            logger.error(f"Error while downloading new version: {str(e)}")
            raise e

