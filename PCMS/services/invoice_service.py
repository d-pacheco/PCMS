import os
import logging

from PCMS.models.invoice_data import InvoiceData
from PCMS.services.google_service import GoogleService
from PCMS.util.file_util import FileUtil

logger = logging.getLogger("pcms")
LAST_JOB_DATA_ROW = 113

class InvoiceService:
    def __init__(
            self,
            file_util: FileUtil,
            google_service: GoogleService,
            template_id: str,
            invoices_dir: str
) -> None:
        self.__file_util = file_util
        self.__gs = google_service
        self.__template_id = template_id
        self.__invoices_dir = invoices_dir

    def create_new_invoice(self, invoice_data: InvoiceData):
        spreadsheet_id = self.__gs.make_copy_of_sheet(self.__template_id, invoice_data.name)
        sheet_id = self.__gs.get_sheet_gid(spreadsheet_id, "Invoice")
        update_requests = [self.__gs.create_write_request(sheet_id, 'G3', invoice_data.invoice_number),
                           self.__gs.create_write_request(sheet_id, 'G4', invoice_data.invoice_date),
                           self.__gs.create_write_request(sheet_id, 'G5', invoice_data.invoice_due_date)]

        # Customer data update requests
        customer_info = invoice_data.customer_info
        update_requests.append(self.__gs.create_write_request(sheet_id, 'A7', customer_info.company_name))
        update_requests.append(self.__gs.create_write_request(sheet_id, 'A8', customer_info.address))

        city_province_postal = f"{customer_info.city}, {customer_info.province}, {customer_info.postal_code}"
        update_requests.append(self.__gs.create_write_request(sheet_id, 'A9', city_province_postal))

        if customer_info.attention is not None:
            update_requests.append(
                self.__gs.create_write_request(sheet_id, 'A10', f"Attention: {customer_info.attention}"))
        else:
            update_requests.append(
                self.__gs.create_write_request(sheet_id, 'A10', ""))

        # Job data update requests
        for index, data in enumerate(invoice_data.job_data):
            row = 14 + (index * 2)  # Starting from A14 and using 2 rows for each item
            update_requests.append(self.__gs.create_write_request(sheet_id, f'A{row}', data.item_id))
            update_requests.append(self.__gs.create_write_request(sheet_id, f'B{row + 1}', data.address))
            update_requests.append(self.__gs.create_write_request(sheet_id, f'E{row}', data.quantity))

        self.__gs.send_batch_requests(spreadsheet_id, update_requests)
        self.__delete_empty_job_data_rows(spreadsheet_id)
        self.__download_invoice_as_pdf(spreadsheet_id, invoice_data.name)

    def __delete_empty_job_data_rows(self, invoice_sheet_id: str):
        last_job_data_row_with_data = self.__gs.get_last_row_with_data(invoice_sheet_id, 'Invoice!A:A')
        self.__gs.delete_rows_in_range(invoice_sheet_id, "Invoice", last_job_data_row_with_data + 1, LAST_JOB_DATA_ROW)

    def __download_invoice_as_pdf(self, invoice_sheet_id: str, invoice_name: str):
        pdf_content = self.__gs.export_sheet_as_pdf(invoice_sheet_id, "Invoice")
        invoice_path = self.__file_util.get_path(self.__invoices_dir)
        pdf_path = os.path.join(invoice_path, f"{invoice_name}.pdf")

        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)

        logger.info(f'Invoice PDF saved as: {pdf_path}')
