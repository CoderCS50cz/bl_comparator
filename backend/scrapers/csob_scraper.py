import requests
from bs4 import BeautifulSoup
import re

def fetch_csob_loan_data() -> dict:
    """Scraper pro Půjčku na cokoliv od ČSOB s parsováním HTML textu."""
    url = "https://www.csob.cz/portal/lide/pujcky/pujcka-na-cokoliv"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "cs-CZ,cs;q=0.9"
    }
    
    fallback_data = {
        "id": "csob",
        "bank_name": "ČSOB",
        "product_name": "Půjčka na cokoliv",
        "logo_url": "assets/csob.png",
        "min_amount": 20000.0,
        "max_amount": 2500000.0,
        "min_duration_months": 12,
        "max_duration_months": 120,
        "interest_rate_from": 6.9,
        "rpsn_from": 7.12,
        "processing_fee": 0.0,
        "monthly_fee": 0.0,
        "web_url": url
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[WARNING ČSOB]: Banka vrátila status {response.status_code}. Používám fallback.")
            return fallback_data
            
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ').lower()
        
        # Hledáme vzorec typu "úrok od X,X %" nebo "sazba od X,X %"
        ir_match = re.search(r'(?:úrok|sazba)\s*(?:od)?\s*([\d,]+)\s*%', page_text)
        
        if ir_match:
            scraped_rate = float(ir_match.group(1).replace(',', '.'))
            fallback_data["interest_rate_from"] = scraped_rate
            print(f"[INFO ČSOB]: Úspěšně naskrapována sazba: {scraped_rate} %")
            
        return fallback_data
        
    except Exception as e:
        print(f"[WARNING ČSOB]: Výpadek spojení ({e}). Používám fallback.")
        return fallback_data