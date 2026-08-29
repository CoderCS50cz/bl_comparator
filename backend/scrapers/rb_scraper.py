import requests

def fetch_rb_loan_data() -> dict:
    """Scraper pro Raiffeisenbank."""
    url = "https://www.rb.cz/osobni/pujcky/minutova-pujcka"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        # requests.get(url, headers=headers)
        return {
            "id": "rb",
            "bank_name": "Raiffeisenbank",
            "product_name": "Minutová půjčka",
            "logo_url": "assets/rb.png",
            "min_amount": 20000.0,
            "max_amount": 1500000.0,
            "min_duration_months": 6,
            "max_duration_months": 120,
            "interest_rate_from": 5.7,
            "rpsn_from": 5.9,
            "processing_fee": 0.0,
            "monthly_fee": 0.0,
            "web_url": url
        }
    except Exception as e:
        print(f"[ERROR RB]: Nepodařilo se načíst data: {e}")
        return None