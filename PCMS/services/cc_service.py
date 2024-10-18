import re
import os
import csv
import logging
from pypdf import PdfReader

from PCMS.models.cc_data import Transaction
from PCMS.util.file_util import FileUtil
from PCMS.util.folder_names import FolderNames

logger = logging.getLogger("pcms")


class CcService:
    __EXCLUDE_KEYWORDS = ['PAYMENT', 'CREDIT', 'REFUND', 'RETURN', 'INTEREST']

    def __init__(self, file_util: FileUtil):
        self.__file_util = file_util


    def process_credit_card_statements(self):
        unprocessed_cc_statement_paths = self.__file_util.get_file_paths(FolderNames.UNPROCESSED_CC_STATEMENTS_FOLDER_NAME)

        if len(unprocessed_cc_statement_paths) == 0:
            logger.info(f"No credit card statements found in {FolderNames.UNPROCESSED_CC_STATEMENTS_FOLDER_NAME} "
                        f"to be processed")
            return None

        for unprocessed_cc_statement_path in unprocessed_cc_statement_paths:
            transactions = self.__get_transactions(unprocessed_cc_statement_path)

            if len(transactions) == 0:
                logger.warning(f"No transactions found inside of {unprocessed_cc_statement_path}")
                continue

            file_name = self.__file_util.get_file_name(unprocessed_cc_statement_path)
            self.__write_transactions_to_csv(FolderNames.GENERATED_CSV_FOLDER_NAME, file_name, transactions)
            self.__file_util.move_file(unprocessed_cc_statement_path, FolderNames.PROCESSED_CC_STATEMENTS_FOLDER_NAME)

    def __get_transactions(self, file_path: str) -> list[Transaction]:
        transaction_lines = self.__read_transactions_from_file(file_path)
        return self.__extract_data_from_transactions(transaction_lines)

    @staticmethod
    def __read_transactions_from_file(file_path: str) -> list[str]:
        reader = PdfReader(file_path)
        combined_lines = []

        for page in reader.pages:
            text = page.extract_text()
            lines = text.split("\n")
            start_index = next((i for i, line in enumerate(lines) if
                                "TRANSACTION POSTINGACTIVITY DESCRIPTION AMOUNT ($)DATE DATE" in line), None)

            if start_index is None:
                continue

            transaction_lines = lines[start_index + 1:]

            combined_line = ""
            for i in range(0, len(transaction_lines) - 1):
                if combined_line == "":
                    combined_line += transaction_lines[i]
                else:
                    combined_line = combined_line + " ||| " + transaction_lines[i]
                if "$" in combined_line:
                    combined_lines.append(combined_line)
                    combined_line = ""

        return combined_lines

    def __extract_data_from_transactions(self, transaction_lines: list[str]) -> list[Transaction]:
        pattern = re.compile(r'(?P<date>\w{3} \d{2})\s+\w{3} \d{2}\s+(?P<name>.+?)\s+\|\|\|.*?(\$[\d,]+\.\d{2})')

        transactions: list[Transaction] = []

        for line in transaction_lines:
            match = pattern.search(line)

            if match:
                date: str = match.group("date")
                description: str = match.group("name").strip()
                amount_str: str = match.group(3)

                amount: float = float(amount_str.replace('$', '').replace(',', ''))

                if not any(keyword in description for keyword in self.__EXCLUDE_KEYWORDS):
                    transactions.append(Transaction(
                        date=date,
                        description=description,
                        amount=amount
                    ))

        return transactions

    def __write_transactions_to_csv(self, folder_name: str, filename: str, transactions: list) -> None:
        """
        Write credit card transactions to a CSV file in a specified folder.

        :param folder_name: The name of the folder to save the CSV file in.
        :param filename: The name of the CSV file (without extension).
        :param transactions: A list of transactions, where each transaction is a tuple (date, description, amount).
        """
        try:
            folder_path = self.__file_util.get_path(folder_name)
            csv_file_path: str = os.path.join(folder_path, f"{filename}.csv")

            max_date_length = max(len(transaction[0]) for transaction in transactions)
            max_description_length = max(len(transaction[1]) for transaction in transactions)
            max_amount_length = max(len(f"${transaction[2]}") for transaction in transactions)

            with open(csv_file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Transaction", "Amount"])

                for transaction in transactions:
                    date, description, amount = transaction

                    centered_date = date.center(max_date_length)
                    centered_description = description.center(max_description_length)
                    centered_amount = f"${amount}".center(max_amount_length)
                    writer.writerow([centered_date, centered_description, centered_amount])

            logger.info(f"Transactions written to {csv_file_path}")

        except Exception as e:
            logger.error(f"Error occurred while writing to the CSV file: {e}")