import logging
import shutil
import sys
from os import makedirs, listdir
from os.path import isfile, join, dirname, abspath, exists, basename

logger = logging.getLogger("pcms")


class FileUtil:
    def __init__(self):
        if not is_running_in_executable():
            # Get the absolute path to the directory containing the script
            curr_dir = dirname(abspath(__file__))
            parent_dir = dirname(curr_dir)
            self.__root_dir = dirname(parent_dir)
        else:
            # Get the absolute path to the directory containing the executable
            self.__root_dir = dirname(sys.executable)

    def get_root(self):
        return self.__root_dir

    def get_path(self, file_or_folder_name: str):
        """
        Gets the absolute path to a given folder name

        :param file_or_folder_name: The name of the file or folder to get absolute path for
        """
        try:
            file_or_folder_path = join(self.__root_dir, file_or_folder_name)
            if not exists(file_or_folder_path):
                raise Exception(f"File or folder {file_or_folder_name} does not exist with the path {file_or_folder_path}")

            return file_or_folder_path
        except Exception as e:
            logger.error(f"Error while getting path for {file_or_folder_name}: {str(e)}")
            raise e

    def file_exists(self, file_name: str) -> bool:
        try:
            file_or_folder_path = join(self.__root_dir, file_name)
            return exists(file_or_folder_path)
        except Exception as e:
            logger.error(f"Error while checking if file {file_name} exists: {str(e)}")
            raise e

    def create_folder(self, folder_name: str) -> None:
        """
        Create a folder if it doesn't already exist.

        :param folder_name: The name of the folder to create.
        """
        folder_path = join(self.__root_dir, folder_name)

        try:
            if not exists(folder_path):
                makedirs(folder_path)
                logger.info(f"Folder created: {folder_path}")
        except Exception as e:
            logger.error(f"An error occurred while creating the folder: {str(e)}")

    def get_file_paths(self, folder_name: str) -> list[str]:
        """
        Get all file paths in the folder

        :param folder_name: The name of the folder to search for files.
        :return: A list of file paths in the folder.
        """
        try:
            folder_path = self.get_path(folder_name)
            return [join(folder_path, file_path) for file_path in listdir(folder_path) if isfile(join(folder_path, file_path))]
        except Exception as e:
            logger.error(f"An error occurred while retrieving file names: {str(e)}")
            return []

    def move_file(self, source_file_path: str, destination_folder: str) -> bool:
        """
        Move a file from one folder to another

        :param source_file_path: The full path of the source file.
        :param destination_folder: The destination folder where the file should be moved.
        :return: True if the file was moved successfully, False otherwise.
        """
        try:
            if not exists(source_file_path):
                logger.error(f"The source file does not exist: {source_file_path}")
                return False

            self.create_folder(destination_folder)
            destination_file_path = join(self.get_path(destination_folder), basename(source_file_path))
            shutil.move(source_file_path, destination_file_path)

            logger.info(f"File moved successfully to: {destination_file_path}")
            return True
        except Exception as e:
            logger.error(f"Error occurred while moving the file: {e}")
            return False


def is_running_in_executable():
    running_in_exe = getattr(sys, 'frozen', False)
    logger.debug(f"Running in exe: {running_in_exe}")
    return running_in_exe
