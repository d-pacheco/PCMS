import customtkinter as ctk

from PCMS.services.cc_service import CcService
from PCMS.services import GoogleService
from PCMS.services import InvoiceService
from PCMS.services.jobber_service import JobberService
from PCMS.util.logger import configure_logger
from PCMS.util.file_util import FileUtil
from PCMS.util.folder_names import FolderNames
from PCMS.util.config import Config, ConfigKeys
from PCMS.GUI.pcms_gui import PcmsGUI
from PCMS.util.version_manager import VersionManager


def create_default_folders(file_util: FileUtil):
    file_util.create_folder(FolderNames.INVOICE_FOLDER)
    file_util.create_folder(FolderNames.PROCESSED_JOB_FOLDER)
    file_util.create_folder(FolderNames.UNPROCESSED_JOB_FOLDER)
    file_util.create_folder(FolderNames.UNPROCESSED_CC_STATEMENTS_FOLDER_NAME)
    file_util.create_folder(FolderNames.PROCESSED_CC_STATEMENTS_FOLDER_NAME)
    file_util.create_folder(FolderNames.GENERATED_CSV_FOLDER_NAME)


def run_gui(
        jobber_servie: JobberService,
        invoice_service: InvoiceService,
        version_manager: VersionManager,
        cc_service: CcService):
    gui = PcmsGUI(jobber_servie, invoice_service, version_manager, cc_service)
    ctk.set_appearance_mode("dark")
    gui.mainloop()

def main():
    file_util = FileUtil()
    config = Config(file_util)
    configure_logger("pcms", file_util, config.get_value(ConfigKeys.DEBUG_LOGGING))
    create_default_folders(file_util)
    version_manager = VersionManager(file_util)


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
    cc_service = CcService(file_util)
    run_gui(jobber_service, invoice_service, version_manager, cc_service)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
