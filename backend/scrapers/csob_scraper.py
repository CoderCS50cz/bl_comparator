from playwright.sync_api import sync_playwright
import time
import re

def generuj_scenare_csob():
    """
    Testovací scénáře generované z Data Pattern Recognition.
    Testujeme jen hlavní hraniční body (20k, 60k, 100k, 500k, 1M, 2.5M).
    """
    scenare = []
    castky = [20000, 60000, 100000, 500000, 1000000, 2500000]
    mesice = [24, 60] 
    
    for c in castky:
        for m in mesice:
            scenare.append({"castka": str(c), "mesice": str(m)})
            
    return scenare

def vycisti_cislo(text: str) -> float:
    """
    Vymaže z textu všechny nesmysly (mezery, Kč, písmena) a převede ho na float.
    Převede např. '20 000 Kč' nebo '60 let' na čisté číslo.
    """
    cislo_str = re.sub(r"[^\d,.]", "", text).replace(",", ".")
    return float(cislo_str) if cislo_str else 0.0

def fetch_csob_loan_data() -> dict:
    print("Spouštím UI robota (Playwright) pro ČSOB (Finální čistá verze)...")
    url = "https://www.csob.cz/lide/pujcky/pujcka-na-cokoliv"

    fallback_data = {
        "id": "csob",
        "bank_name": "ČSOB",
        "product_name": "Půjčka na cokoliv",
        "logo_url": "assets/csob.png",
        "min_amount": 20000.0,
        "max_amount": 2500000.0,
        "min_duration_months": 12,
        "max_duration_months": 120,
        "interest_rate_from": 4.99, 
        "rpsn_from": 5.1,
        "processing_fee": 0.0,
        "monthly_fee": 0.0,
        "web_url": url,
        "rate_card": []
    }

    testovaci_scenare = generuj_scenare_csob()
    print(f"[INFO CSOB] Bude otestováno {len(testovaci_scenare)} unikátních kombinací.")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(locale="cs-CZ")
            page.goto(url, timeout=60000)

            # Odkliknutí Cookies
            try:
                page.get_by_role("button", name="Použít jen technické cookies", exact=True).click(timeout=3000)
            except:
                pass

            # Zaměření vstupních polí podle štítků (nejspolehlivější pro ČSOB)
            castka_input = page.get_by_role("textbox", name="Kolik si chci půjčit", exact=True)
            roky_input = page.get_by_role("textbox", name="Jak dlouho chcete splácet?", exact=True)
            
            castka_input.wait_for(state="visible", timeout=15000)

            nejnizsi_urok = 99.9
            nejnizsi_rpsn = 99.9
            zpracovane_kombinace = set() 

            for scenar in testovaci_scenare:
                try:
                    # 1. Vyplnění Částky
                    castka_input.click(timeout=5000)
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.keyboard.type(scenar["castka"])
                    page.keyboard.press("Tab") 
                    time.sleep(0.3)

                    # 2. Vyplnění Měsíců (ČSOB políčko sice píše "Roky", ale interně chce roky)
                    roky_input.click(timeout=5000)
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    mesice_int = int(scenar["mesice"])
                    roky_input.type(str(mesice_int // 12)) 
                    page.keyboard.press("Tab")

                    time.sleep(1.5) # Čekáme na asynchronní přepočet sazeb

                    # 3. ZPĚTNÉ ČTENÍ Z POLÍČEK (vyčištění textu od "Kč", "let" a mezer)
                    skutecna_castka = vycisti_cislo(castka_input.input_value())
                    skutecne_roky = vycisti_cislo(roky_input.input_value())
                    
                    if skutecna_castka == 0 or skutecne_roky == 0:
                        continue
                        
                    skutecne_mesice = int(skutecne_roky * 12)
                    
                    unikatni_klic = f"{skutecna_castka}-{skutecne_mesice}"
                    if unikatni_klic in zpracovane_kombinace:
                        continue

                    # 4. ČTENÍ SAZEB ZE STRÁNKY
                    vysledek_kontejner = page.locator(".rct-b-calculator-spa-interest-example")
                    page_text = vysledek_kontejner.inner_text().replace('\n', ' ').replace('\xa0', ' ')
                    
                    rate_match = re.search(r"úrokové sazby\s+(\d+(?:[,.]\d+)?)\s*%", page_text, re.IGNORECASE)
                    rpsn_match = re.search(r"RPSN\s+(\d+(?:[,.]\d+)?)\s*%", page_text, re.IGNORECASE)

                    if rate_match and rpsn_match:
                        sazba = vycisti_cislo(rate_match.group(1))
                        rpsn = vycisti_cislo(rpsn_match.group(1))

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
                        print(f"CSOB OK: {skutecna_castka} Kč / {skutecne_mesice} m -> Úrok {sazba} % | RPSN {rpsn} %")
                    else:
                        print(f"CSOB VAROVÁNÍ: Úroková sazba nenalezena.")
                    
                    time.sleep(0.5)
                    
                except Exception as iter_err:
                    print(f"CSOB CHYBA při iteraci {scenar['castka']}: {iter_err}")

            browser.close()

            if nejnizsi_urok != 99.9:
                fallback_data["interest_rate_from"] = nejnizsi_urok
                fallback_data["rpsn_from"] = nejnizsi_rpsn

            print(f"[INFO CSOB] Hotovo. Nasbíráno {len(fallback_data['rate_card'])} kombinací.")

    except Exception as e:
        print(f"[ERROR CSOB] Kritická chyba robota: {e}")

    return fallback_data