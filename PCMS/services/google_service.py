import logging
import os
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from PCMS.util.file_util import FileUtil

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

logger = logging.getLogger("pcms")


class GoogleService:
    def __init__(self, file_util: FileUtil, credentials_file_name: str):
        self.__file_util = file_util
        self.__creds = self.__authenticate_with_oauth(credentials_file_name)
        self.__drive_service = build('drive', 'v3', credentials=self.__creds)
        self.__sheet_service = build('sheets', 'v4', credentials=self.__creds)

    def __authenticate_with_oauth(self, credentials_file_name: str):
        try:
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first time.
            if self.__file_util.file_exists("token.json"):
                token_file_path = self.__file_util.get_path("token.json")
                creds = Credentials.from_authorized_user_file(token_file_path, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    creds_file_path = self.__file_util.get_path(credentials_file_name)
                    flow = InstalledAppFlow.from_client_secrets_file(creds_file_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(f"{self.__file_util.get_root()}/token.json", 'w') as token:
                    token.write(creds.to_json())

            return creds
        except Exception as e:
            logger.error(f"Error while authenticating with OAuth: {str(e)}")

    def make_copy_of_sheet(self, spreadsheet_id: str, new_name: str):
        """
        Creates a copy of an existing spreadsheet.

        :param spreadsheet_id: The ID of the spreadsheet to create a copy of.
        :param new_name: The name of the newly created spreadsheet.
        """
        try:
            logger.info(f"Creating a copy of spreadsheet with ID {spreadsheet_id} with new name {new_name}")
            body = {
                'name': new_name,
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            }
            response = self.__drive_service.files().copy(fileId=spreadsheet_id, body=body).execute()
            new_sheet_id = response['id']
            logger.info(f"Copied File ID: {new_sheet_id}")
            return new_sheet_id
        except Exception as e:
            logger.error(f"Error when making copy of spreadsheet with ID {spreadsheet_id} with name {new_name}: {str(e)}")
            raise e

    @staticmethod
    def create_write_request(sheet_id: str, range_name: str, value: str) -> dict:
        """
        Create an update request to be used in a batch update request call.

        :param sheet_id: The ID of the sheet inside the spreadsheet to target.
        :param range_name: The range of cells to be updated.
        :param value: The value to update the cells with.
        """
        return {
            'updateCells': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': get_row_from_range(range_name),
                    'endRowIndex': get_row_from_range(range_name) + 1,
                    'startColumnIndex': get_col_from_range(range_name),
                    'endColumnIndex': get_col_from_range(range_name) + 1
                },
                'rows': [{'values': [{'userEnteredValue': {'stringValue': value}}]}],
                'fields': 'userEnteredValue'
            }
        }

    def export_sheet_as_pdf(self, spreadsheet_id: str, sheet_name: str) -> bytes:
        """
        Returns the spreadsheet exported as a pdf in bytes

        :param spreadsheet_id: The ID of the spreadsheet to be turned into a PDF.
        :param sheet_name: The name of the sheet inside the spreadsheet to be exported.
        """
        try:
            gid = self.get_sheet_gid(spreadsheet_id, sheet_name)
            pdf_export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=pdf&gid={gid}"

            headers = {
                'Authorization': f'Bearer {self.__creds.token}',
            }
            response = requests.get(pdf_export_url, headers=headers)

            if response.status_code == 200:
                return response.content
            else:
                logger.error(
                    f"None 200 code while exporting the sheet {sheet_name} from spreadsheet with ID {spreadsheet_id} "
                    f"as a PDF: {response.content}")
        except Exception as e:
            logger.error(
                f"Error when export as PDF spreadsheet with ID {spreadsheet_id} with "
                f"sheet name {sheet_name}: {str(e)}")
            raise e

    def get_last_row_with_data(self, spreadsheet_id: str, data_range: str) -> int:
        """
        Get the last row number that has data within a range.

        :param spreadsheet_id: The ID of the Google Sheet.
        :param data_range: The range to look for data.
        """
        try:
            result = self.__sheet_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=data_range
            ).execute()
            return len(result.get('values', []))
        except Exception as e:
            logger.error(
                f"Error when getting last row with data spreadsheet with ID {spreadsheet_id} "
                f"with data range {data_range}: {str(e)}")
            raise e

    def delete_rows_in_range(self, spreadsheet_id: str, sheet_name: str, start_row: int, end_row: int) -> None:
        """
        Deletes rows in the specified range from the Google Sheet.

        :param spreadsheet_id: The ID of the Google Sheet.
        :param sheet_name: The name of the sheet inside the spreadsheet to have its rows deleted.
        :param start_row: The starting row (inclusive) for deletion.
        :param end_row: The ending row (inclusive) for deletion.
        """
        total_rows = self.__get_sheets_total_rows(spreadsheet_id, sheet_name)

        if end_row > total_rows:
            logger.info(f"End row {end_row} exceeds the total number of rows ({total_rows}).")
            return

        if start_row > total_rows:
            logger.info(f"No rows to delete. Starting row {start_row} exceeds the total number of rows ({total_rows}).")
            return

        gid = self.get_sheet_gid(spreadsheet_id, sheet_name)

        delete_requests = [
            {
                'deleteDimension': {
                    'range': {
                        'sheetId': gid,
                        'dimension': 'ROWS',
                        'startIndex': start_row,
                        'endIndex': end_row
                    }
                }
            }
        ]

        logger.info(f"Sending request to deleted rows from {start_row} to {end_row}.")
        self.send_batch_requests(spreadsheet_id, delete_requests)

    def send_batch_requests(self, spreadsheet_id: str, update_requests: list) -> None:
        """
        Send a batched update request to Google Sheets

        :param spreadsheet_id: The ID of the Google Sheet.
        :param update_requests: The list of batched update requests
        :return None
        """

        try:
            body = {
                'requests': update_requests
            }
            self.__sheet_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            logger.debug(f"Batch update successful. Requests sent: {len(update_requests)}")
        except Exception as e:
            logger.error(f"Error when sending batch update to spreadsheet with ID {spreadsheet_id}: {str(e)}")
            raise e

    def get_sheet_gid(self, spreadsheet_id: str, sheet_name: str):
        """
        Get the GID of a sheet within a spreadsheet

        :param spreadsheet_id: The ID of the Google Sheet.
        :param sheet_name: The name of the sheet inside the spreadsheet
        """
        try:
            spreadsheet = self.__sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            raise ValueError(f"Sheet with name '{sheet_name}' not found.")
        except Exception as e:
            logger.error(f"Error getting sheet gid (spreadsheet_id: {spreadsheet_id}, sheet_name: {sheet_name}): {str(e)}")
            raise e

    def __get_sheets_total_rows(self, spreadsheet_id: str, sheet_name: str) -> int:
        """
        Get the total number of rows within a sheet

        :param spreadsheet_id: The ID of the Google Sheet.
        :param sheet_name: The name of the sheet inside the spreadsheet
        """
        try:
            sheet_metadata = self.__sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet_properties = next(
                (sheet for sheet in sheet_metadata.get('sheets', []) if
                 sheet.get('properties', {}).get('title') == sheet_name),
                None
            )

            if sheet_properties:
                total_rows = sheet_properties.get('properties', {}).get('gridProperties', {}).get('rowCount', 0)
                return total_rows
            else:
                logger.info(f'Sheet "{sheet_name}" not found.')
                return 0
        except Exception as e:
            logger.error(f"Error while getting total sheet rows (spreadsheet_id: {spreadsheet_id}, sheet_name: {sheet_name} {str(e)}")
            raise e

def get_row_from_range(range_name: str):
    """
    Helper function to parse the row from the range string
    e.g. 'G3' -> 3

    :param range_name: The range to get the row index of
    """
    return int(''.join([char for char in range_name if char.isdigit()])) - 1

def get_col_from_range(range_name: str):
    """
    Helper function to parse the column from the range string
    e.g. 'G3' -> G -> 6

    :param range_name: The range to get the col index of
    """
    col_letter = ''.join([char for char in range_name if char.isalpha()]).upper()
    return ord(col_letter) - ord('A')
