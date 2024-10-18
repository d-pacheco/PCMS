import logging
import requests
import platform
from os.path import join

from PCMS.util.file_util import FileUtil


logger = logging.getLogger("pcms")


class VersionManager:
    __LATEST_RELEASE_URL = "https://api.github.com/repos/d-pacheco/pcms/releases/latest"
    __CURRENT_VERSION = 0.9

    def __init__(self, file_util: FileUtil):
        self.__file_util = file_util
        latest_release_response = requests.get(self.__LATEST_RELEASE_URL)
        self.__latest_release_info: dict = latest_release_response.json()

    def is_latest_version(self) -> bool:
        latest_version_tag = self.__latest_release_info.get("tag_name", None)
        if latest_version_tag is not None:
            latest_version = float(latest_version_tag[1:])
        else:
            latest_version = 0.0
        return self.__CURRENT_VERSION >= latest_version

    def download_latest_version(self):
        system_type = get_system_info()
        version_number = self.__latest_release_info['tag_name'].lstrip('v')

        asset_map = {
            'windows': 'PCMS_windows.exe',
            'intel': 'PCMS_intel',
            'arm': 'PCMS_arm'
        }

        asset_name = asset_map.get(system_type)
        if not asset_name:
            logger.warning(f"Unsupported system type: {system_type}")
            return

        asset_url = next(
            (asset['browser_download_url']
             for asset in self.__latest_release_info['assets']
             if asset['name'] == asset_name), None)
        if asset_url is None:
            logger.warning(f"No download available for {system_type}")
            return

        filename = f"{asset_name.rsplit('.', 1)[0]}_v{version_number}.{asset_name.rsplit('.', 1)[1]}"
        logger.info(f"Downloading {system_type} version from {asset_url}")
        response = requests.get(asset_url)

        file_path = join(self.__file_util.get_root(), filename)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        logger.info(f"{system_type} version downloaded successfully as {filename}.")

def get_system_info():
    system = platform.system().lower()
    architecture = platform.machine().lower()

    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        if 'arm' in architecture:
            return 'arm'
        else:
            return 'intel'
    else:
        raise Exception("Unsupported operating system")
