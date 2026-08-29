from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, HttpUrl

class BankLoanProduct(BaseModel):
    id: str
    bank_name: str
    product_name: str
    logo_url: str
    min_amount: float
    max_amount: float
    min_duration_months: int
    max_duration_months: int
    interest_rate_from: float
    rpsn_from: float
    processing_fee: float = 0.0
    monthly_fee: float = 0.0
    web_url: str

class LoanDataCollection(BaseModel):
    last_updated: str
    currency: str = "CZK"
    banks: List[BankLoanProduct]

def get_utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()