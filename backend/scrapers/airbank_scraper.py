from playwright.sync_api import sync_playwright
import time
import re

def vycisti_cislo(text: str) -> float:
    cislo_str = re.sub(r"[^\d,.]", "", text).replace(",", ".")
    return float(cislo_str) if cislo_str else 0.0

def fetch_airbank_loan_data() -> dict:
    print("Spouštím UI robota (Playwright) pro Air Bank (Zjednodušený průchod slideru)...")
    url = "https://www.airbank.cz/produkty/pujcka/"

    fallback_data = {
        "id": "airbank",
        "bank_name": "Air Bank",
        "product_name": "Půjčka",
        "logo_url": "assets/airbank.png",
        "min_amount": 20000.0,
        "max_amount": 1200000.0, # Necháváme rezervu, bude upraveno podle webu
        "min_duration_months": 6,
        "max_duration_months": 110,
        "interest_rate_from": 4.4, 
        "rpsn_from": 4.49,
        "processing_fee": 0.0,
        "monthly_fee": 0.0,
        "web_url": url,
        "rate_card": []
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(locale="cs-CZ")
            page.goto(url, timeout=60000)

            # Odkliknutí Cookies
            try:
                page.get_by_role("button", name="Odmítnout vše", exact=True).click(timeout=3000)
            except:
                pass

            # 1. NAČTENÍ MAXIMÁLNÍ VÝŠE ÚVĚRU Z WEBU
            print("Zjišťuji maximální možný úvěr z banky...")
            amount_slider = page.get_by_role("slider", name="Kolik potřebujete půjčit?", exact=True)
            amount_slider.wait_for(state="visible", timeout=15000)
            
            try:
                # Vytažení aria atributu (mnohem spolehlivější než Regex textu)
                max_amt = float(amount_slider.get_attribute("aria-valuemax"))
                if max_amt > 20000:
                    fallback_data["max_amount"] = max_amt
            except:
                pass

            # 2. NASTAVENÍ POSUVNÍKU SAZEB NA MINIMUM
            print("Hledám úrokové sazby...")
            rate_slider = page.get_by_role("slider", name="Úroková sazba", exact=True)
            rate_slider.click()
            
            # Srolujeme na minimum pomocí klávesy Home
            rate_slider.press("Home")
            time.sleep(1) 
            
            zpracovane_sazby = set()
            nejnizsi_urok = 99.9
            nejnizsi_rpsn = 99.9

            # 3. KROKOVÁNÍ SLIDERU
            for i in range(15): # Ochrana proti nekonečné smyčce
                
                # Vyčtení aktuální sazby z test_id atributu (mnohem stabilnější čtení)
                try:
                    sazba_text = page.get_by_test_id("loan-calculator-interest-rate").inner_text()
                    rpsn_text = page.get_by_test_id("loan-calculator-rpsn").inner_text()
                    
                    sazba = vycisti_cislo(sazba_text)
                    rpsn = vycisti_cislo(rpsn_text)

                    if sazba > 0 and sazba not in zpracovane_sazby:
                        zpracovane_sazby.add(sazba)
                        fallback_data["rate_card"].append({
                            # Přidáme povinné hodnoty pro Pydantic model (frontend je pro Air Bank ignoruje)
                            "amount": 0.0, 
                            "months": 0,
                            "interest_rate": sazba,
                            "rpsn": rpsn
                        })
                        print(f"AIRBANK SAZBA: Nalezen úrok {sazba} % | RPSN {rpsn} %")
                        
                        if sazba < nejnizsi_urok:
                            nejnizsi_urok = sazba
                        if rpsn < nejnizsi_rpsn:
                            nejnizsi_rpsn = rpsn
                except Exception as eval_err:
                    print("Drobná chyba při čtení aktuální polohy slideru:", eval_err)

                # Přečteme, kde fyzicky slider je, abychom poznali, jestli už není na konci
                aktualni_hodnota_slideru = rate_slider.get_attribute("aria-valuenow")
                maximalni_hodnota_slideru = rate_slider.get_attribute("aria-valuemax")
                
                if aktualni_hodnota_slideru == maximalni_hodnota_slideru:
                    print("Dosaženo maximální sazby, ukončuji krokování.")
                    break
                    
                # Posun o krok doprava
                rate_slider.press("ArrowRight")
                time.sleep(0.5) # Drobné zpoždění na zpracování animace

            browser.close()

            if fallback_data["rate_card"]:
                fallback_data["interest_rate_from"] = nejnizsi_urok
                fallback_data["rpsn_from"] = nejnizsi_rpsn

            print(f"[INFO AIRBANK] Hotovo. Nalezeno {len(fallback_data['rate_card'])} variant sazeb.")

    except Exception as e:
        print(f"[ERROR AIRBANK] Kritická chyba robota: {e}")

    return fallback_data