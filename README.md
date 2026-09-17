# Srovnávač bankovních úvěrů (Proof of Concept)

Tento repozitář obsahuje prototyp webové aplikace (Proof of Concept) pro automatizované srovnávání a výpočet bankovních úvěrů. Aplikace vznikla jako praktická část diplomové práce studenta Smirnova Iaroslava studujicího obor Informatika kombinované formy na Provozně ekonomické fakultě České zemědělské univerzity v Praze (PEF ČZU).

Cílem aplikace návrhu a realizace prototypu webové aplikace pro automatizované srovnávání a výpočet bankovních úvěrů je demonstrovat hybridní architekturu (Jamstack), která řeší problematiku nedostupnosti otevřených API (PSD2) pro úvěrové produkty a obchází aktivní blokace ze strany bankovních firewallů (WAF).

## 🛠 Použité technologie
* **Backend (Sběr dat a validace):** Python 3.x, `requests`, `BeautifulSoup4`, `re`, `pydantic`
* **Datová vrstva:** Statický JSON
* **Frontend (Klientská logika):** HTML5, CSS3, Vanilla JavaScript

## 📂 Struktura projektu

```text
bank-loan-comparator/
│
├── backend/
│   ├── scrapers/          # Skripty pro jednotlivé banky (CSAS, Air Bank, RB, ČSOB, KB)
│   ├── main.py            # Hlavní spouštěcí skript pro sběr dat
│   ├── utils.py           # Pomocné funkce a datové modely (Pydantic)
│   └── requirements.txt   # Závislosti pro Python knihovny
│
├── data/
│   └── loans_data.json    # Vygenerovaná databáze marketingových sazeb
│
├── frontend/
│   ├── css/style.css      # Uživatelské rozhraní (NerdWallet style)
│   ├── js/
│   │   ├── app.js         # Hlavní logika srovnávače, filtrace a interakce
│   │   ├── calculator.js  # Matematický model pro výpočet anuitní splátky
│   │   └── comparator.js  # Rozšiřující logika srovnávače
│   └── index.html         # Hlavní webová stránka
│
├── .gitignore             # Ignorované soubory pro Git
├── AGENTS.md              # Konfigurace agentů / AI dokumentace
└── README.md              # Tato dokumentace
```

⚙️ Architektura a Metodika
Aplikace záměrně nevyužívá živé proxy dotazování do interních bankovních systémů (risk-based pricing) z důvodu porušování obchodních podmínek, vysoké latence a blokování ze strany WAF.
Místo toho využívá dvoufázový model:

Sběr dat: Python skripty lokálně stáhnou HTML stránky 5 hlavních českých bank, pomocí regulárních výrazů extrahují inzerované startovní sazby („úrok od“), zvalidují data přes Pydantic modely a uloží je do JSON souboru. Skripty jsou vybaveny fallback mechanismem pro případ výpadku nebo blokace spojení.

Klientský výpočet: JavaScriptový frontend načte statická data a veškeré přepočty měsíčních splátek (anuitní vzorec) provádí v reálném čase přímo v prohlížeči uživatele.

🚀 Návod ke spuštění
1. Příprava prostředí
Ujistěte se, že máte nainstalovaný Python 3.x. V terminálu nainstalujte potřebné knihovny pomocí souboru requirements.txt, který se nachází ve složce backend:

pip install -r backend/requirements.txt

2. Spuštění sběru dat (Aktualizace sazeb)
Pro stažení nejnovějších úrokových sazeb z webů bank a jejich validaci spusťte z kořenového adresáře projektu tento příkaz:

python backend/main.py

Úspěšné spuštění vygeneruje (nebo přepíše) soubor data/loans_data.json.

3. Spuštění webové aplikace
Aby frontend správně načítal data ze složky data/, je nutné aplikaci spustit přes lokální webový server. V kořenovém adresáři spusťte příkaz:

python -m http.server 8000

Následně si otevřete webový prohlížeč a přejděte na adresu:
http://localhost:8000/frontend/

(Poznámka: Pokud se po úpravách neprojeví změny v designu, proveďte tvrdé obnovení stránky pomocí zkratky Ctrl + F5 pro smazání cache prohlížeče).