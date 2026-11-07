from playwright.sync_api import sync_playwright
import time
import re

def generuj_scenare_rb():
    """
    Vygeneruje seznam testovacích scénářů (kombinace částky a doby splácení)
    specificky pro Raiffeisenbank na základě dřívější datové analýzy (Data Pattern Recognition).
    """
    scenare = []
    castky = [20000, 50000, 100000, 200000, 2000000]
    mesice = [24, 72, 120] 
    
    for c in castky:
        for m in mesice:
            scenare.append({"castka": str(c), "mesice": str(m)})
            
    return scenare

def fetch_rb_loan_data() -> dict:
    """
    Hlavní funkce pro spuštění UI robota, který projde web Raiffeisenbank,
    zadá požadované hodnoty do kalkulačky a přečte výsledné úroky a RPSN.
    """
    print("Spouštím UI robota pro Raiffeisenbank (Zjednodušená čistá verze)...")
    url = "https://www.rb.cz/osobni/pujcky/minutova-pujcka"

    fallback_data = {
        "id": "rb",
        "bank_name": "Raiffeisenbank",
        "product_name": "Minutová půjčka",
        "logo_url": "assets/rb.png",
        "min_amount": 5000.0,
        "max_amount": 2000000.0,
        "min_duration_months": 3,
        "max_duration_months": 120,
        "interest_rate_from": 4.9, 
        "rpsn_from": 5.0,
        "processing_fee": 0.0,
        "monthly_fee": 0.0,
        "web_url": url,
        "rate_card": []
    }

    testovaci_scenare = generuj_scenare_rb()
    print(f"Bude otestováno celkem {len(testovaci_scenare)} kombinací.")

    try:
        with sync_playwright() as p:
            # Headless=True znamená, že prohlížeč běží skrytě (rychlejší a stabilnější)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)

            # Odkliknutí Cookies
            try:
                page.get_by_role("button", name="Jen nezbytné cookies").click(timeout=3000)
            except:
                pass

            # KALKULAČKA JE V IFRAME (vložené okno)
            iframe_selector = 'iframe[src^="https://pujcka.rb.cz"]'
            page.wait_for_selector(iframe_selector, timeout=15000)
            kalkulacka = page.frame_locator(iframe_selector)

            # Zaměření vstupních polí podle ID (naprosto přesné)
            amount_input = kalkulacka.locator("#calc-amount")
            months_input = kalkulacka.locator("#calc-instalments")
            
            amount_input.wait_for(state="visible", timeout=15000)

            nejnizsi_urok = 99.9
            nejnizsi_rpsn = 99.9
            zpracovane_kombinace = set() 

            for scenar in testovaci_scenare:
                # 1. Vyplnění Částky
                amount_input.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(scenar["castka"])
                page.keyboard.press("Enter")
                page.keyboard.press("Tab") 
                time.sleep(0.5)

                # 2. Vyplnění Měsíců
                months_input.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(scenar["mesice"])
                page.keyboard.press("Enter")
                page.keyboard.press("Tab")

                # Čekáme, až banka asynchronně přepočítá úrok
                time.sleep(1.5) 

                # 3. ZPĚTNÉ ČTENÍ
                skutecna_castka_str = amount_input.input_value().replace(' ', '').replace('\xa0', '')
                skutecne_mesice_str = months_input.input_value().replace(' ', '').replace('\xa0', '')
                
                if not skutecna_castka_str or not skutecne_mesice_str:
                    continue
                    
                skutecna_castka = float(skutecna_castka_str)
                skutecne_mesice = int(skutecne_mesice_str)
                
                unikatni_klic = f"{skutecna_castka}-{skutecne_mesice}"
                if unikatni_klic in zpracovane_kombinace:
                    continue

                # 4. ČTENÍ SAZEB - OPRAVA PROBLÉMU S ODŘÁDKOVÁNÍM
                # Nahradíme všechny \n (Entery) a nezlomitelné mezery normální mezerou
                page_text = kalkulacka.locator("body").inner_text().replace('\n', ' ').replace('\xa0', ' ')
                
                # Regex si nyní hladce najde cestu z textu k číslu
                rate_match = re.search(r'(?:Roční úroková sazba|Úroková sazba od|Úroková sazba|Úrok).*?(\d+[,.]\d{1,2})\s*%', page_text, re.IGNORECASE)
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
                    
                    print(f"RB OK: {skutecna_castka} Kč / {skutecne_mesice} m -> Úrok {sazba} % | RPSN {rpsn} %")
                else:
                    print(f"RB VAROVÁNÍ: Sazba pro {skutecna_castka} Kč nenalezena na obrazovce.")
                
                time.sleep(0.5)

            browser.close()

            if nejnizsi_urok != 99.9:
                fallback_data["interest_rate_from"] = nejnizsi_urok
                fallback_data["rpsn_from"] = nejnizsi_rpsn

            print(f"[INFO RB] Hotovo. Nasbíráno {len(fallback_data['rate_card'])} unikátních kombinací sazeb.")

    except Exception as e:
        print(f"[ERROR RB] Chyba robota: {e}")

    return fallback_data