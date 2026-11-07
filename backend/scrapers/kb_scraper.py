from playwright.sync_api import sync_playwright
import time
import re

def generuj_scenare_kb():
    """
    Vygeneruje testovací matici pro Komerční banku na základě Data Pattern Recognition.
    Otestujeme přesně 21 kombinací z optimalizované tabulky, abychom prošli přes WAF.
    """
    scenare = []
    
    # 7 hranic pro změnu úrokové sazby podle tabulky
    castky = [20000, 50000, 100000, 250000, 400000, 1000000, 2500000]
    # Tři vzorkové doby pro ověření fixace sazby
    mesice = [12, 60, 96] 
    
    for c in castky:
        for m in mesice:
            scenare.append({"castka": str(c), "mesice": str(m)})
            
    return scenare

def fetch_kb_loan_data() -> dict:
    """
    Spustí jednoduchého, spolehlivého robota pro Komerční banku,
    který funguje na stejném principu jako CSAS a RB scraper.
    """
    print("Spouštím UI robota pro Komerční banku (Čistá verze)...")
    url = "https://www.kb.cz/cs/obcane/pujcky/osobni-pujcka"

    fallback_data = {
        "id": "kb",
        "bank_name": "Komerční banka",
        "product_name": "Osobní půjčka",
        "logo_url": "assets/kb.png",
        "min_amount": 10000.0,
        "max_amount": 2500000.0,
        "min_duration_months": 12,
        "max_duration_months": 96,
        "interest_rate_from": 4.99, 
        "rpsn_from": 5.13,
        "processing_fee": 0.0,
        "monthly_fee": 0.0,
        "web_url": url,
        "rate_card": []
    }

    testovaci_scenare = generuj_scenare_kb()
    print(f"Bude otestováno optimalizovaných {len(testovaci_scenare)} kombinací.")

    try:
        with sync_playwright() as p:
            # Pro produkci nebo stabilitu necháváme headless=True
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)

            # 1. Agresivní odkliknutí Cookies (pokud tam je)
            try:
                page.get_by_role("button", name="Jen nezbytné").click(timeout=3000)
            except:
                pass

            # 2. Kliknutí na úvodní tlačítko "Spočítat", které KB někdy vyžaduje
            try:
                page.get_by_role("link", name="Spočítat", exact=True).click(timeout=3000)
            except:
                pass

            # 3. ZAMĚŘENÍ POLÍČEK (Využíváme přesné Angular/LWC selektory z banky)
            print("Čekám na načtení interní kalkulačky...")
            amount_input = page.locator('lwc-unit-input[formcontrolname="loanAmount"] input').first
            months_input = page.locator('lwc-unit-input[formcontrolname="maturity"] input').first

            amount_input.wait_for(state="visible", timeout=15000)
            
            # Najdeme i výpočetní tlačítko
            submit_button = page.locator('button[type="submit"]:has-text("Spočítat")').first

            nejnizsi_urok = 99.9
            nejnizsi_rpsn = 99.9
            zpracovane_kombinace = set() 

            for scenar in testovaci_scenare:
                try:
                    # Vyplnění Částky
                    amount_input.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.keyboard.type(scenar["castka"])
                    page.keyboard.press("Tab")
                    time.sleep(0.3)

                    # Vyplnění Měsíců
                    months_input.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.keyboard.type(scenar["mesice"])
                    page.keyboard.press("Tab")
                    
                    # KB často vyžaduje fyzický klik na tlačítko k zahájení výpočtu
                    try:
                        submit_button.click(timeout=2000)
                    except:
                        pass

                    # Čekání na asynchronní přepočet KB
                    time.sleep(1.5) 

                    # Zpětné čtení
                    skutecna_castka_str = amount_input.input_value().replace(' ', '').replace('\xa0', '')
                    skutecne_mesice_str = months_input.input_value().replace(' ', '').replace('\xa0', '')
                    
                    if not skutecna_castka_str or not skutecne_mesice_str:
                        continue
                        
                    skutecna_castka = float(skutecna_castka_str)
                    skutecne_mesice = int(skutecne_mesice_str)
                    
                    unikatni_klic = f"{skutecna_castka}-{skutecne_mesice}"
                    if unikatni_klic in zpracovane_kombinace:
                        continue

                    # ČTENÍ VÝSLEDKU (Omezíme se jen na kontejner kalkulačky)
                    page_text = page.locator("#clc-calculator").inner_text().replace('\n', ' ').replace('\xa0', ' ')
                    
                    # Regex pro KB, zachytí "Pevná úroková sazba" i jen "Úroková sazba"
                    rate_match = re.search(r'(?:Pevná úroková sazba|Úroková sazba).*?(\d+[,.]\d{1,2})\s*%', page_text, re.IGNORECASE)
                    rpsn_match = re.search(r'RPSN.*?(\d+[,.]\d{1,2})\s*%', page_text, re.IGNORECASE)

                    if rate_match and rpsn_match:
                        sazba = float(rate_match.group(1).replace(',', '.'))
                        rpsn = float(rpsn_match.group(1).replace(',', '.'))

                        if sazba < nejnizsi_urok:
                            nejnizsi_urok = sazba
                        if rpsn < nejnizsi_rpsn:
                            nejnizsi_rpsn = rpsn

                        fallback_data["rate_card"].append({
                            "amount": skutecna_castka,
                            "months": skutecne_mesice,
                            "interest_rate": sazba,
                            "rpsn": rpsn
                        })
                        zpracovane_kombinace.add(unikatni_klic)
                        
                        print(f"KB OK: {skutecna_castka} Kč / {skutecne_mesice} m -> Úrok {sazba} % | RPSN {rpsn} %")
                    else:
                        print(f"KB VAROVÁNÍ: Sazba pro {skutecna_castka} Kč nenalezena.")
                    
                    # Malá ochrana proti WAF blokaci mezi iteracemi
                    time.sleep(0.5)
                    
                except Exception as iter_err:
                    print(f"KB CHYBA při iteraci {scenar['castka']}: {iter_err}")

            browser.close()

            if nejnizsi_urok != 99.9:
                fallback_data["interest_rate_from"] = nejnizsi_urok
                fallback_data["rpsn_from"] = nejnizsi_rpsn

            print(f"[INFO KB] Hotovo. Nasbíráno {len(fallback_data['rate_card'])} unikátních kombinací sazeb.")

    except Exception as e:
        print(f"[ERROR KB] Chyba robota: {e}")

    return fallback_data