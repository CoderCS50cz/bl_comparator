import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_airbank_loan_data() -> dict:
    """Scraper pro Air Bank s extrakcí Next.js Hydration state."""
    url = "https://www.airbank.cz/produkty/pujcka/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Hledání konfiguračního JSONu vloženého přímo do HTML
        next_data_tag = soup.find("script", id="__NEXT_DATA__")
        
        if next_data_tag:
            # Převedení tagu na Python slovník (validace JSON struktury)
            app_state = json.loads(next_data_tag.string)
            
            # Pro vyhledávání hluboko zanořených hodnot v dynamickém CMS
            # je technicky stabilnější převést JSON zpět na text a použít Regex
            state_str = json.dumps(app_state)
            
            # Hledáme např. "interestRate": 4.4 nebo "rpsn": 4.49
            ir_match = re.search(r'"interestRate"\s*:\s*([\d.]+)', state_str)
            rpsn_match = re.search(r'"rpsn"\s*:\s*([\d.]+)', state_str)
            
            # Pokud se hodnoty podaří vyčíst z dat webu, použijí se. 
            # Jinak použijeme fallback hodnoty z vašeho screenshotu.
            interest_rate = float(ir_match.group(1)) if ir_match else 4.4
            rpsn = float(rpsn_match.group(1)) if rpsn_match else 4.49
            
            return {
                "id": "airbank",
                "bank_name": "Air Bank",
                "product_name": "Půjčka",
                "logo_url": "assets/airbank.png",
                "min_amount": 5000.0,
                "max_amount": 2000000.0,
                "min_duration_months": 6,
                "max_duration_months": 120,
                "interest_rate_from": interest_rate,
                "rpsn_from": rpsn,
                "processing_fee": 0.0,
                "monthly_fee": 0.0,
                "web_url": url
            }
        else:
            print("[ERROR AirBank]: Skrytý __NEXT_DATA__ JSON nebyl na stránce nalezen.")
            return None
            
    except Exception as e:
        print(f"[ERROR AirBank]: Nepodařilo se načíst data: {e}")
        return None