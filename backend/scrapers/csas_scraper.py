import requests
from bs4 import BeautifulSoup

def fetch_csas_loan_data() -> dict:
    """Scraper pro Českou spořitelnu."""
    url = "https://www.csas.cz/cs/osobni-finance/pujcky/pujcka"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return {
            "id": "csas",
            "bank_name": "Česká spořitelna",
            "product_name": "Půjčka",
            "logo_url": "assets/csas.png",
            "min_amount": 2000.0,
            "max_amount": 2500000.0,
            "min_duration_months": 6,
            "max_duration_months": 108,
            "interest_rate_from": 3.91,
            "rpsn_from": 4.03,
            "processing_fee": 0.0,
            "monthly_fee": 0.0,
            "web_url": url
        }
    except Exception as e:
        print(f"[ERROR CSAS]: Nepodařilo se načíst data: {e}")
        return None