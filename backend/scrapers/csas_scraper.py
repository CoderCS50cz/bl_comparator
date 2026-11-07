from playwright.sync_api import sync_playwright
import time
import re

def generuj_scenare():
    scenare = []
    
    # 1. Pásmo: Malé půjčky (max 96 měsíců)
    for c in [20000, 50000]:
        for m in [6, 48, 60, 72, 84, 96]:
            scenare.append({"castka": str(c), "mesice": str(m)})
            
    # 2. Pásmo: 100 000 Kč (max 96 měsíců, objevuje se sweet-spot 4.38 %)
    for m in [6, 48, 60, 72, 84, 96]:
        scenare.append({"castka": "100000", "mesice": str(m)})
        
    # 3. Pásmo: 200 000 Kč (otevírá se 108 měsíců)
    for m in [6, 48, 60, 72, 84, 96, 108]:
        scenare.append({"castka": "200000", "mesice": str(m)})
        
    # 4. Pásmo: Velké půjčky (identické křivky, max 120 měsíců)
    # Z mé tabulky vidím, že 700k je stejné jako 1M, takže testujeme jen reprezentativní vzorky
    for c in [500000, 1000000, 2500000]:
        for m in [6, 48, 60, 72, 84, 96, 108, 120]:
            scenare.append({"castka": str(c), "mesice": str(m)})
            
    return scenare

def fetch_csas_loan_data() -> dict:
    print("Spouštím UI robota pro Českou spořitelnu (Pokročilá matice)...")
    url = "https://www.csas.cz/cs/osobni-finance/pujcky/pujcka"

    fallback_data = {
        "id": "csas",
        "bank_name": "Česká spořitelna",
        "product_name": "Půjčka",
        "logo_url": "assets/csas.png",
        "min_amount": 2000.0,
        "max_amount": 2500000.0,
        "min_duration_months": 6,
        "max_duration_months": 120,
        "interest_rate_from": 4.48, 
        "rpsn_from": 4.64,
        "processing_fee": 0.0,
        "monthly_fee": 0.0,
        "web_url": url,
        "rate_card": []
    }

    testovaci_scenare = generuj_scenare()
    print(f"Bude otestováno celkem {len(testovaci_scenare)} kombinací.")

    try:
        with sync_playwright() as p:
            # Pro ostrý běh na GitHubu (Netlify) MUSÍ být headless=True
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)

            # Odkliknutí Cookies
            try:
                page.locator("text='Přijmout vše'").click(timeout=3000)
            except:
                pass

            page.wait_for_selector("input", timeout=10000)
            inputs = page.locator("input")

            nejnizsi_urok = 99.9
            nejnizsi_rpsn = 99.9
            zpracovane_kombinace = set() # Pro zamezení duplikátů (např. když UI opraví více extrémů na stejnou hodnotu)

            for scenar in testovaci_scenare:
                # 1. Vyplnění požadované částky
                inputs.nth(0).click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(scenar["castka"])
                page.keyboard.press("Enter")
                time.sleep(0.5)

                # 2. Vyplnění požadovaných měsíců
                inputs.nth(1).click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(scenar["mesice"])
                page.keyboard.press("Enter")

                # Čekáme, až banka přes JavaScript přepočítá úrok
                time.sleep(1.5) 

                # 3. ZPĚTNÉ ČTENÍ (Read-back): Zjistíme, jak hodnoty po zadání web upravil
                # (Odstraníme mezery u milionů, např. "2 500 000" -> "2500000")
                skutecna_castka_str = inputs.nth(0).input_value().replace(' ', '').replace('\xa0', '')
                skutecne_mesice_str = inputs.nth(1).input_value().replace(' ', '').replace('\xa0', '')
                
                # Ošetření prázdných hodnot při chybě načtení
                if not skutecna_castka_str or not skutecne_mesice_str:
                    continue
                    
                skutecna_castka = float(skutecna_castka_str)
                skutecne_mesice = int(skutecne_mesice_str)
                
                # Vytvoření unikátního klíče. Pokud už jsme tuto kombinaci kvůli auto-korekci webu uložili, přeskočíme ji.
                unikatni_klic = f"{skutecna_castka}-{skutecne_mesice}"
                if unikatni_klic in zpracovane_kombinace:
                    continue

                # 4. Čtení výsledné sazby
                page_text = page.locator("body").inner_text()
                rate_match = re.search(r'Úroková sazba od\s+(\d+[,.]\d{1,2})\s*%', page_text, re.IGNORECASE)
                rpsn_match = re.search(r'RPSN\s+(\d+[,.]\d{1,2})\s*%', page_text, re.IGNORECASE)

                if rate_match and rpsn_match:
                    sazba = float(rate_match.group(1).replace(',', '.'))
                    rpsn = float(rpsn_match.group(1).replace(',', '.'))

                    # Uložení nejnižší sazby pro hlavní kartu
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
                    
                    print(f"CSAS OK: {skutecna_castka} Kč / {skutecne_mesice} m -> Úrok {sazba} % | RPSN {rpsn} %")
                
                # Záměrná drobná pauza, abychom omezili riziko WAF blokace
                time.sleep(0.5)

            browser.close()

            # Přepis výchozích dat tím nejlepším nalezeným
            if nejnizsi_urok != 99.9:
                fallback_data["interest_rate_from"] = nejnizsi_urok
                fallback_data["rpsn_from"] = nejnizsi_rpsn

            print(f"[INFO CSAS] Hotovo. Nasbíráno {len(fallback_data['rate_card'])} unikátních kombinací sazeb.")

    except Exception as e:
        print(f"[ERROR CSAS] Chyba robota: {e}")

    return fallback_data