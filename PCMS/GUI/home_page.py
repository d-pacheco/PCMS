import customtkinter as ctk
import logging

from PCMS.models.invoice_data import CustomerInfo, InvoiceData
from PCMS.services.cc_service import CcService
from PCMS.services.jobber_service import JobberService
from PCMS.services.invoice_service import InvoiceService
from PCMS.util.config import Config, ConfigKeys
from PCMS.util.file_util import FileUtil

logger = logging.getLogger("pcms")


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller, jobber_service: JobberService, invoice_service: InvoiceService, cc_service: CcService):
        super().__init__(parent)
        file_util = FileUtil()
        self.config = Config(file_util)
        self.jobber_service = jobber_service
        self.invoice_service = invoice_service
        self.cc_service = cc_service

        label = ctk.CTkLabel(self, text="Home Page", font=("Helvetica", 24))
        label.pack(pady=20)

        button1 = ctk.CTkButton(self, text="Go to Page One",
                                 command=lambda: controller.show_frame("PageOne"))
        button1.pack(pady=10)

        cc_button = ctk.CTkButton(self, text="Process CC Statements", command=self.start_processing_cc_statements)
        cc_button.pack(pady=10)

        invoice_button = ctk.CTkButton(self, text="Generate Invoice",command=self.start_generating_invoice)
        invoice_button.pack(pady=10)

        self.info_label = ctk.CTkLabel(self, text="", font=("Helvetica", 12))
        self.info_label.pack(pady=5)

    def start_processing_cc_statements(self):
        self.info_label.configure(text="Processing CC Statements...")
        try:
            statements_processed = self.cc_service.process_credit_card_statements()
            if statements_processed is None:
                self.info_label.configure(text="No CC statements to be processed")
            else:
                self.info_label.configure(text="CC Statements Processed Successfully")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            self.info_label.configure(text="Error", text_color="red")

    def start_generating_invoice(self):
        self.info_label.configure(text="Generating Invoice...")
        try:
            job_data_generated = self.generate_invoice()
            if job_data_generated is None:
                self.info_label.configure(text="No Jobs to be processed")
            else:
                self.info_label.configure(text="Invoice Generated Successfully")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            self.info_label.configure(text="Error", text_color="red")

    def generate_invoice(self):
        job_data = self.jobber_service.process_jobber_pdfs()
        if job_data is None:
            return None
        if self.config.get_value(ConfigKeys.BILLED_COMPANY_ATTENTION) == '':
            customer_info = CustomerInfo(
                company_name = self.config.get_value(ConfigKeys.BILLED_COMPANY_NAME),
                address = self.config.get_value(ConfigKeys.BILLED_COMPANY_ADDRESS),
                city = self.config.get_value(ConfigKeys.BILLED_COMPANY_CITY),
                province = self.config.get_value(ConfigKeys.BILLED_COMPANY_PROVINCE),
                postal_code = self.config.get_value(ConfigKeys.BILLED_COMPANY_POSTAL_CODE)
            )
        else:
            customer_info = CustomerInfo(
                company_name=self.config.get_value(ConfigKeys.BILLED_COMPANY_NAME),
                address=self.config.get_value(ConfigKeys.BILLED_COMPANY_ADDRESS),
                city=self.config.get_value(ConfigKeys.BILLED_COMPANY_CITY),
                province=self.config.get_value(ConfigKeys.BILLED_COMPANY_PROVINCE),
                postal_code=self.config.get_value(ConfigKeys.BILLED_COMPANY_POSTAL_CODE),
                attention=self.config.get_value(ConfigKeys.BILLED_COMPANY_ATTENTION)
            )

        invoice_data = InvoiceData(
            name = "Test Invoice 30",
            invoice_number = "00069",
            invoice_date = "10/14/2024",
            invoice_due_date = "10/20/2024",
            customer_info = customer_info,
            job_data = job_data
        )
        self.invoice_service.create_new_invoice(invoice_data)
        self.jobber_service.move_processed_jobs()
        return job_data
