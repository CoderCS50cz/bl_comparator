import requests

def fetch_csob_loan_data() -> dict:
    """Scraper pro ČSOB."""
    url = "https://www.csob.cz/portal/lide/pujcky/pujcka-na-cokoliv"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        # requests.get(url, headers=headers)
        return {
            "id": "csob",
            "bank_name": "ČSOB",
            "product_name": "Půjčka na cokoliv",
            "logo_url": "assets/csob.png",
            "min_amount": 20000.0,
            "max_amount": 1200000.0,
            "min_duration_months": 12,
            "max_duration_months": 96,
            "interest_rate_from": 6.9,
            "rpsn_from": 7.1,
            "processing_fee": 0.0,
            "monthly_fee": 0.0,
            "web_url": url
        }
    except Exception as e:
        print(f"[ERROR CSOB]: Nepodařilo se načíst data: {e}")
        return None