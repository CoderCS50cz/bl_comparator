import requests

def fetch_kb_loan_data() -> dict:
    """Scraper pro Komerční banku."""
    url = "https://www.kb.cz/cs/obcane/pujcky/osobni-pujcka"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        # requests.get(url, headers=headers)
        return {
            "id": "kb",
            "bank_name": "Komerční banka",
            "product_name": "Osobní půjčka",
            "logo_url": "assets/kb.png",
            "min_amount": 10000.0,
            "max_amount": 2500000.0,
            "min_duration_months": 12,
            "max_duration_months": 96,
            "interest_rate_from": 6.5,
            "rpsn_from": 6.7,
            "processing_fee": 0.0,
            "monthly_fee": 0.0,
            "web_url": url
        }
    except Exception as e:
        print(f"[ERROR KB]: Nepodařilo se načíst data: {e}")
        return None