import json
from pathlib import Path
from scrapers.csas_scraper import fetch_csas_loan_data
from scrapers.airbank_scraper import fetch_airbank_loan_data
from scrapers.rb_scraper import fetch_rb_loan_data
from scrapers.csob_scraper import fetch_csob_loan_data
from scrapers.kb_scraper import fetch_kb_loan_data

from utils import BankLoanProduct, LoanDataCollection, get_utc_now_iso

def main():
    print("Spouštím automatizovaný sběr dat o úvěrech...")
    
    raw_products = [
        fetch_csas_loan_data(),
        fetch_airbank_loan_data(),
        fetch_rb_loan_data(),
        fetch_csob_loan_data(),
        fetch_kb_loan_data()
    ]
    
    valid_products = []
    for item in raw_products:
        if item:
            try:
                product = BankLoanProduct(**item)
                valid_products.append(product)
            except Exception as val_err:
                print(f"[VALIDATION ERROR]: {val_err}")

    data_collection = LoanDataCollection(
        last_updated=get_utc_now_iso(),
        banks=valid_products
    )

    output_path = Path(__file__).parent.parent / "data" / "loans_data.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_collection.model_dump(), f, ensure_ascii=False, indent=2)
        
    print(f"Data byla úspěšně uložena do: {output_path.resolve()}")

if __name__ == "__main__":
    main()