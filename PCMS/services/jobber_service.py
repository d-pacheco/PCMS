import logging
from pypdf import PdfReader

from PCMS.models.invoice_data import JobData
from PCMS.util.jobber_util import ITEM_MAP, valid_job_item
from PCMS.util.file_util import FileUtil

logger = logging.getLogger("pcms")


class JobberService:
    def __init__(self, file_util: FileUtil, unprocessed_job_dir_name: str, processed_job_dir_name: str):
        self.__file_util = file_util
        self.__unprocessed_job_dir_name = unprocessed_job_dir_name
        self.__processed_job_dir_name = processed_job_dir_name

    def process_jobber_pdfs(self) -> list or None:
        results = []

        jobber_pdf_paths = self.__file_util.get_file_paths(self.__unprocessed_job_dir_name)
        if len(jobber_pdf_paths) == 0:
            logger.warning(f"NO JOBS FOUND TO BE PROCESSED")
            return None

        for jobber_pdf_path in jobber_pdf_paths:
            results.extend(get_job_data_from_pdf(jobber_pdf_path))

        return results

    def move_processed_jobs(self) -> None:
        jobber_pdf_paths = self.__file_util.get_file_paths(self.__unprocessed_job_dir_name)
        for jobber_pdf_path in jobber_pdf_paths:
            self.__file_util.move_file(jobber_pdf_path, self.__processed_job_dir_name)


def get_job_data_from_pdf(jobber_pdf_path: str) -> list[JobData]:
    try:
        reader = PdfReader(jobber_pdf_path)
        page = reader.get_page(0)
        text = page.extract_text()
        lines = text.split("\n")

        address = get_service_address(lines)
        items_and_quantities = get_item_numbers_and_quantities(lines)

        results = []
        for items_and_quantity in items_and_quantities:
            results.append(
                JobData(
                    item_id=items_and_quantity[0],
                    address=address,
                    quantity=str(items_and_quantity[1])
                )
            )
            results.append(
                JobData(
                    item_id=items_and_quantity[0]+"I",
                    address=address,
                    quantity=str(items_and_quantity[1])
                )
            )

        return results
    except Exception as e:
        logger.error(f"Error getting job data from pdf {jobber_pdf_path}: {str(e)}")
        raise e

def get_service_address(page_lines: list[str]):
    start_index = get_address_starting_index(page_lines)
    if start_index is None:
        raise Exception("Could not find a valid starting address index")

    address_lines = []
    for line in page_lines[start_index:]:
        if "Job #" in line:
            address_lines.append(line.split("Job #")[0].strip())
            break
        address_lines.append(line.strip())

    service_address = ", ".join(address_lines)
    return service_address

def get_address_starting_index(page_lines: list[str]) -> int or None:
    service_address_index = get_index_of_text(page_lines, "SERVICE ADDRESS:")
    if service_address_index is not None:
        return service_address_index + 1

    recipient_address_index = get_index_of_text(page_lines, "RECIPIENT:")
    if recipient_address_index is not None:
        return recipient_address_index + 2

    return None

def get_item_numbers_and_quantities(lines: list[str]) -> list[tuple[str, int]]:
    results = []
    start_index = get_index_of_text(lines, "Product/Service Description Qty.")
    assert (start_index is not None)

    for line in lines[start_index + 1:]:
        if not valid_job_item(line):
            break

        parts = line.split()  # Normalize spaces (removes multiple spaces, ensures single space between parts)
        # Handle cases like "3 ft" by joining the ft value with the number
        if parts[1] == "ft":
            parts[1] = parts[0] + parts[1]  # Join the number and "ft"
            parts.pop(0)  # Remove the number part (as it's now joined)

        # Rebuild the description from the normalized parts
        if "ft" in parts[1]:
            description = " ".join(parts[1:-1]).lower()
        else:
            description = " ".join(parts[:-1]).lower()
        if "support" in description:
            description = description.replace("support", "straight")
        quantity = int(parts[-1])
        item_number = ITEM_MAP.get(description)

        if item_number:
            results.append((item_number, quantity))
        else:
            raise Exception(f"Could not find item number for item with description: {description}")

    return results

def get_index_of_text(str_list: list[str], target_str: str) -> int or None:
    return next((i for i, line in enumerate(str_list) if target_str in line), None)
