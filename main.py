from PCMS.services import GoogleService
from PCMS.services import InvoiceService
from PCMS.models.invoice_data import InvoiceData, CustomerInfo, JobData
from PCMS.services.jobber_service import JobberService
from PCMS.util.logger import configure_logger
from PCMS.util.file_util import FileUtil
from PCMS.util.folder_names import FolderNames
from PCMS.util.config import Config, ConfigKeys


def create_default_folders(file_util: FileUtil):
    file_util.create_folder(FolderNames.INVOICE_FOLDER)
    file_util.create_folder(FolderNames.PROCESSED_JOB_FOLDER)
    file_util.create_folder(FolderNames.UNPROCESSED_JOB_FOLDER)

def main():
    file_util = FileUtil()
    config = Config(file_util)
    configure_logger("pcms", file_util, config.get_value(ConfigKeys.DEBUG_LOGGING))



    create_default_folders(file_util)
    google_service = GoogleService(
        file_util,
        config.get_value(ConfigKeys.AUTH_CRED_FILE_NAME)
    )
    invoice_service = InvoiceService(
        file_util,
        google_service,
        config.get_value(ConfigKeys.TEMPLATE_SPREADSHEET_ID),
        FolderNames.INVOICE_FOLDER
    )
    jobber_service = JobberService(
        file_util,
        FolderNames.UNPROCESSED_JOB_FOLDER,
        FolderNames.PROCESSED_JOB_FOLDER
    )
    job_data = jobber_service.process_jobber_pdfs()
    if job_data is None:
        return

    if config.get_value(ConfigKeys.BILLED_COMPANY_ATTENTION) == '':
        customer_info = CustomerInfo(
            company_name = config.get_value(ConfigKeys.BILLED_COMPANY_NAME),
            address = config.get_value(ConfigKeys.BILLED_COMPANY_ADDRESS),
            city = config.get_value(ConfigKeys.BILLED_COMPANY_CITY),
            province = config.get_value(ConfigKeys.BILLED_COMPANY_PROVINCE),
            postal_code = config.get_value(ConfigKeys.BILLED_COMPANY_POSTAL_CODE)
        )
    else:
        customer_info = CustomerInfo(
            company_name=config.get_value(ConfigKeys.BILLED_COMPANY_NAME),
            address=config.get_value(ConfigKeys.BILLED_COMPANY_ADDRESS),
            city=config.get_value(ConfigKeys.BILLED_COMPANY_CITY),
            province=config.get_value(ConfigKeys.BILLED_COMPANY_PROVINCE),
            postal_code=config.get_value(ConfigKeys.BILLED_COMPANY_POSTAL_CODE),
            attention=config.get_value(ConfigKeys.BILLED_COMPANY_ATTENTION)
        )

    invoice_data = InvoiceData(
        name = "Test Invoice 26",
        invoice_number = "00069",
        invoice_date = "10/14/2024",
        invoice_due_date = "10/20/2024",
        customer_info = customer_info,
        job_data = job_data
    )
    invoice_service.create_new_invoice(invoice_data)
    jobber_service.move_processed_jobs()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
