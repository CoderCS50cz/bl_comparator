import requests
from bs4 import BeautifulSoup
import re

def fetch_rb_loan_data() -> dict:
    """Scraper pro Minutovou půjčku od Raiffeisenbank s parsováním HTML textu."""
    url = "https://www.rb.cz/osobni/pujcky/minutova-pujcka"
    
    # Hlavička prohlížeče, aby web neblokoval pythoní skript
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "cs-CZ,cs;q=0.9"
    }
    
    # Záložní hodnoty pro případ výpadku nebo blokace
    fallback_data = {
        "id": "rb",
        "bank_name": "Raiffeisenbank",
        "product_name": "Minutová půjčka",
        "logo_url": "assets/rb.png",
        "min_amount": 5000.0,
        "max_amount": 2000000.0,
        "min_duration_months": 3,
        "max_duration_months": 120,
        "interest_rate_from": 4.7,
        "rpsn_from": 5.02,
        "processing_fee": 0.0,
        "monthly_fee": 0.0,
        "web_url": url
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[WARNING RB]: Banka vrátila status {response.status_code}. Používám fallback.")
            return fallback_data
            
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ').lower()
        
        # Hledáme vzorec typu "úroková sazba od X,X %" nebo "od X,X % p.a."
        ir_match = re.search(r'(?:úroková sazba|úrok)\s*(?:od)?\s*([\d,]+)\s*%', page_text)
        
        if ir_match:
            scraped_rate = float(ir_match.group(1).replace(',', '.'))
            fallback_data["interest_rate_from"] = scraped_rate
            print(f"[INFO RB]: Úspěšně naskrapována sazba: {scraped_rate} %")
            
        return fallback_data
        
    except Exception as e:
        print(f"[WARNING RB]: Výpadek spojení ({e}). Používám fallback.")
        return fallback_data