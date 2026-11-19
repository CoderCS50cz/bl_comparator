from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

# Model pro jednu položku v úrokové matici (testovací scénář)
class RateCardItem(BaseModel):
    amount: float
    months: int
    interest_rate: float
    rpsn: float

# Hlavní model definující datovou strukturu bankovního produktu
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
    processing_fee: float
    monthly_fee: float
    web_url: str
    # Napojení na úrokovou matici pomocí striktní validace přes seznam
    rate_card: Optional[List[RateCardItem]] = None

class LoanDataCollection(BaseModel):
    last_updated: str
    currency: str = "CZK"
    banks: List[BankLoanProduct]

def get_utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()