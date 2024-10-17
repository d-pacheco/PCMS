from pydantic import BaseModel


class CustomerInfo(BaseModel):
    company_name: str
    address: str
    city: str
    province: str
    postal_code: str
    attention: str or None = None


class JobData(BaseModel):
    item_id: str
    address: str
    quantity: str


class InvoiceData(BaseModel):
    name: str
    invoice_number: str
    invoice_date: str
    invoice_due_date: str
    customer_info: CustomerInfo
    job_data: list[JobData]
