import requests
from bs4 import BeautifulSoup
import re

def fetch_csas_loan_data() -> dict:
    url = "https://www.csas.cz/cs/osobni-finance/pujcky/pujcka"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # Výchozí záložní hodnoty pro případ výpadku spojení
    fallback_data = {
        "id": "csas",
        "bank_name": "Česká spořitelna",
        "product_name": "Půjčka",
        "logo_url": "assets/csas.png",
        "min_amount": 2000.0,
        "max_amount": 2500000.0,
        "min_duration_months": 6,
        "max_duration_months": 108,
        "interest_rate_from": 3.99,
        "rpsn_from": 4.15,
        "processing_fee": 0.0,
        "monthly_fee": 0.0,
        "web_url": url
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[WARNING CSAS]: Stránka vrátila status {response.status_code}, používám fallback.")
            return fallback_data
            
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ')
        
        # Hledání fráze typu "s úrokem od 3,99" nebo podobných obměn v textu stránky
        rate_match = re.search(r'úrokem od\s*([\d,]+)\s*%', page_text, re.IGNORECASE)
        
        if rate_match:
            scraped_rate = float(rate_match.group(1).replace(',', '.'))
            fallback_data["interest_rate_from"] = scraped_rate
            print(f"[INFO CSAS]: Úspěšně naskrapována sazba: {scraped_rate} %")
        
        return fallback_data
        
    except Exception as e:
        print(f"[WARNING CSAS]: Chyba při scrapingu ({e}), používám fallback.")
        return fallback_data