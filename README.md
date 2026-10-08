# 🏦 FinTech Web Scraper & Bank Loan Comparator

> **Technologický prototyp (Proof of Concept) webového srovnávače a kalkulačky bankovních úvěrů v ČR.**  
> Vypracováno v rámci diplomové práce na Provozně ekonomické fakultě ČZU v Praze (Katedra informačního inženýrství) studentem Smirnovym Iaroslavem.

🌐 **Živá aplikace (Netlify):** [https://srovnavac-pef-czu.netlify.app](https://srovnavac-pef-czu.netlify.app)

---

## 📌 O projektu

Aplikace řeší problém uzavřenosti bankovních API v oblasti spotřebitelských úvěrů. Kombinuje automatizovaný sběr veřejně dostupných marketingových sazeb z webových stránek 5 významných českých bank s klientskou kalkulačkou anuitního splácení.

### Podporované bankovní domy:
* 🔵 **Česká spořitelna**
* 🟡 **Raiffeisenbank**
* 🟢 **Air Bank**
* 🔵 **ČSOB**
* 🔴 **Komerční banka**

---

## 🏗️ Softwarová architektura (Jamstack)

Projekt využívá kompozitní architekturu typu **Jamstack** s odděleným backendem a frontendem. Celý systém běží automatizovaně s nulovými provozními náklady:

1. **Backend (Python 3.11):**
   * Automatické stahování HTML stránek bank (`requests` s imitací hlaviček `User-Agent`).
   * Extrakce úrokových sazeb z DOM struktury (regulární výrazy a `BeautifulSoup`).
   * Striktní typová kontrola a validace dat pomocí knihovny `Pydantic`.
   * Bezpečnostní fallback mechanismus pro případ výpadku webu banky nebo blokace (WAF).
   * Generování výstupního datového JSON souboru (`frontend/data/loans_data.json`).

2. **CI/CD Automatizace (GitHub Actions):**
   * Plně bezobslužný chod. Konfigurační workflow (`.github/workflows/scraper.yml`) nastartuje izolovaný virtuální server (Ubuntu) každý den o půlnoci (Cron).
   * Spustí Python skript, detekuje změny úrokových sazeb a pokud se trh změnil, robot (GitHub Action Bot) aplikuje automatický commit a push do hlavní větvě repozitáře.

3. **Frontend & Deployment (Netlify):**
   * Responzivní klientská aplikace s designem inspirovaným lídry na trhu (HTML5, CSS3, Vanilla JS).
   * Výpočetní logika anuitního splácení, řazení bank a přepočet RPSN probíhá asynchronně přímo v prohlížeči (Client-Side Rendering).
   * **Continuous Deployment:** Jakmile GitHub Actions upraví JSON soubor s daty (`frontend/data/loans_data.json`), platforma Netlify to okamžitě detekuje a automaticky publikuje novou verzi webu na produkční adrese.

---

## 📁 Struktura projektu

```text
bank-loan-comparator/
├── .github/
│   └── workflows/
│       └── scraper.yml         # CI/CD automatizace pro GitHub Actions
├── backend/
│   ├── scrapers/               # Jednotlivé moduly pro extrakci dat
│   │   ├── airbank_scraper.py
│   │   ├── csas_scraper.py
│   │   ├── csob_scraper.py
│   │   ├── kb_scraper.py
│   │   └── rb_scraper.py
│   ├── main.py                 # Řídící skript spouštějící všechny scrapování
│   ├── requirements.txt        # Závislosti Pythonu pro virtuální prostředí
│   └── utils.py                # Konfigurace hlaviček a Pydantic modely
├── frontend/
│   ├── assets/                 # Statické grafické podklady
│   ├── css/
│   │   └── style.css           # Kaskádové styly klientské aplikace
│   ├── data/
│   │   └── loans_data.json     # Výstupní agregovaný datový soubor
│   ├── js/
│   │   ├── app.js              # Fetch dat, DOM manipulace a vykreslení karet
│   │   ├── calculator.js       # Implementace vzorce anuitního splácení
│   │   └── comparator.js       # Logika filtrace a řazení
│   └── index.html              # Hlavní uživatelské rozhraní kalkulačky
└── README.md
```

## 🚀 Lokální spuštění a vývoj
Pokud si chcete projekt spustit a upravovat lokálně na vlastním počítači:

### 1. Spuštění backendového scraperu:
```bash
# Vytvoření a aktivace virtuálního prostředí (volitelné)
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Instalace požadovaných závislostí
pip install -r backend/requirements.txt

# Ruční spuštění sběru aktuálních dat z bank
python backend/main.py
```

### 2. Spuštění lokálního webového serveru:
```bash
# Nastartování lokálního HTTP serveru
python -m http.server 8000
```

Aplikace bude dostupná ve vašem prohlížeči na adrese: http://localhost:8000/frontend/

## 👨‍💻 Autor a vedení práce
Autor: Ing. Jaroslav Smirnov

Vedoucí práce: Ing. Josef Pavlíček, Ph.D.

Akademické pracoviště: Katedra informačního inženýrství, Provozně ekonomická fakulta ČZU v Praze