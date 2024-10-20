import logging
import configparser
import os

from PCMS.util.file_util import FileUtil


class ConfigKeys:
    AUTH_CRED_FILE_NAME = 'auth_cred_file_name'
    TEMPLATE_SPREADSHEET_ID = 'template_spreadsheet_id'
    BILLED_COMPANY_NAME = 'billed_company_name'
    BILLED_COMPANY_ADDRESS = 'billed_company_address'
    BILLED_COMPANY_CITY = 'billed_company_city'
    BILLED_COMPANY_PROVINCE = 'billed_company_province'
    BILLED_COMPANY_POSTAL_CODE = 'billed_company_postal_code'
    BILLED_COMPANY_ATTENTION = 'billed_company_attention'
    DEBUG_LOGGING = 'debug_logging'


DEFAULT_SECTION = 'Default'
CONFIG_FILE_NAME = 'config.cfg'
DEFAULT_CONFIG = {
    ConfigKeys.AUTH_CRED_FILE_NAME: 'auth_creds.json',
    ConfigKeys.TEMPLATE_SPREADSHEET_ID: '',
    ConfigKeys.BILLED_COMPANY_NAME: '',
    ConfigKeys.BILLED_COMPANY_ADDRESS: '',
    ConfigKeys.BILLED_COMPANY_CITY: '',
    ConfigKeys.BILLED_COMPANY_PROVINCE: '',
    ConfigKeys.BILLED_COMPANY_POSTAL_CODE: '',
    ConfigKeys.BILLED_COMPANY_ATTENTION: '',
    ConfigKeys.DEBUG_LOGGING: False
}

logger = logging.getLogger("pcms")


class Config:
    def __init__(self, file_util: FileUtil):
        self.__file_util = file_util
        self.config = configparser.ConfigParser()

        if not self.__file_util.file_exists(CONFIG_FILE_NAME):
            logger.info(f"Could not find config file in {self.__file_util.get_root()}")
            self.create_default_config()
        self.config.read(self.__file_util.get_path(CONFIG_FILE_NAME))
        self.verify_config_file()

    def create_default_config(self):
        logger.info("Creating config file with default values")
        self.config[DEFAULT_SECTION] = DEFAULT_CONFIG
        self.save_config_file()

    def save_config_file(self):
        logger.info("Saving config file")
        config_path = os.path.join(self.__file_util.get_root(), CONFIG_FILE_NAME)
        with open(config_path, 'w') as config_file:
            self.config.write(config_file)

    def verify_config_file(self):
        logger.info("Validating config file")
        valid_config = True
        if self.config.has_section(DEFAULT_SECTION):
            for key in DEFAULT_CONFIG:
                if not self.config.has_option(DEFAULT_SECTION, key):
                    logger.warning(f"Config file missing option {key}")
                    # populate the config with the option and default value if not present
                    self.config[DEFAULT_SECTION][key] = str(DEFAULT_CONFIG[key])
                    valid_config = False
        else:
            logger.warning("Config file missing default section")
            self.create_default_config()  # re-create the entire config if the section is wrong

        if not valid_config:
            self.save_config_file()  # Needed to make changed to config file, save those changes

    def get_value(self, value: str):
        try:
            # Attempt to get the value as a boolean first
            return self.config.getboolean(DEFAULT_SECTION, value)
        except ValueError:
            # If it can't be interpreted as a boolean, return as a string
            return self.config.get(DEFAULT_SECTION, value)
