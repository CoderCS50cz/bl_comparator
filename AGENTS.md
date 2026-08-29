# Bank Loan Comparator - AI Agent Instructions

## Project Overview

**Purpose:** Czech bank loan comparison tool that automatically scrapes loan offers from multiple Czech banks and provides an interactive calculator for users to compare loan products based on amount and duration.

**Target Users:** Czech-speaking users comparing personal loans.

---

## Architecture

### Directory Structure
```
backend/          # Python data collection & validation
├── main.py       # Entry point: orchestrates scrapers, validates, outputs JSON
├── utils.py      # Pydantic data models
└── scrapers/     # Bank-specific scraper modules
    ├── csas_scraper.py, airbank_scraper.py, etc.
    └── __init__.py

frontend/         # Vanilla JavaScript web UI
├── index.html    # Main UI with input form & results
├── js/
│   ├── app.js    # Fetch JSON, render & filter results
│   └── calculator.js  # Annuity calculation logic
└── css/style.css # (Currently empty)

data/
└── loans_data.json # Generated output (5 banks with rates & terms)
```

### Data Flow
1. **Backend Pipeline:** Run `python main.py` → scrapers fetch bank data → Pydantic validates → writes JSON
2. **Frontend:** Load `loans_data.json` → User inputs loan params → JavaScript filters & calculates → Display results

---

## Setup & Build

### Backend (Data Collection)
```bash
cd backend
pip install -r requirements.txt
python main.py
```
- **Output:** `data/loans_data.json` (list of loan products with rates, terms, fees)
- **Requirements:** Python 3.x, Requests, BeautifulSoup4, Pydantic ≥2.0.0

### Frontend (Web UI)
```bash
# From project root, serve via HTTP (required for CORS/file:// safety)
python -m http.server 8000
# OR: npx http-server

# Open browser: http://localhost:8000/frontend/index.html
```
- **Important:** Must serve over HTTP (not file://), otherwise JSON loading fails
- No build/compile step needed (vanilla HTML/CSS/JS)

---

## Key Files & Responsibilities

| File | Purpose | Notes |
|------|---------|-------|
| [backend/main.py](backend/main.py) | Entry point; import & run all scrapers | Run to regenerate `loans_data.json` |
| [backend/utils.py](backend/utils.py) | Pydantic models: `BankLoanProduct`, `LoanDataCollection` | Schema & validation source of truth |
| [backend/scrapers/](backend/scrapers/) | Bank-specific data fetchers | Each follows same pattern: `fetch_[bank]_loan_data()` |
| [frontend/index.html](frontend/index.html) | UI: input fields, results container | Edit form fields or result layout here |
| [frontend/js/app.js](frontend/js/app.js) | Load JSON, fetch bank data, filter & render results | Core business logic for frontend |
| [frontend/js/calculator.js](frontend/js/calculator.js) | Annuity formula for monthly payment calculation | Math: `payment = principal × (r(1+r)^n) / ((1+r)^n - 1)` |
| [data/loans_data.json](data/loans_data.json) | Generated output (5 banks with current rates) | Auto-generated; do not edit manually |

---

## Development Conventions

### Python (Backend)

**Naming:**
- Snake_case for functions: `fetch_csas_loan_data()`, `validate_loan_data()`
- PascalCase for Pydantic models: `BankLoanProduct`, `LoanDataCollection`
- Bank IDs are lowercase: `csas`, `airbank`, `csob`, `kb`, `rb`

**Scraper Pattern:**
Each scraper module follows this pattern:
```python
def fetch_[bank]_loan_data() -> dict | None:
    """Fetch loan data for [Bank].
    Returns dict matching BankLoanProduct schema, or None on error.
    """
    try:
        # Use requests.get() with headers (User-Agent required)
        # Parse HTML with BeautifulSoup or return mock data
        # Return validated dict or None
    except Exception as e:
        print(f"Error fetching [bank] data: {e}")
        return None
```

**Data Validation:**
- All scraped data validated through Pydantic before saving
- Invalid entries logged; pipeline continues (fail-gracefully)
- `LoanDataCollection.model_dump_json()` for JSON output

**Comments:** Czech language acceptable for domain-specific comments; English for code explanations.

### JavaScript (Frontend)

**Naming:**
- camelCase for functions: `fetchLoanData()`, `filterLoansByAmount()`
- LOAN_PARAMS, BANK_COLORS for constants

**Patterns:**
- Fetch JSON at page load → store in global state
- Event listeners on form inputs trigger filter & recalculate
- `calculator.js` provides pure function `calculateMonthlyPayment()`
- Render results by building HTML strings or DOM manipulation

**No Frameworks:** Vanilla JS only; no React, Vue, or build step.

---

## Common Tasks

### Adding a New Bank Scraper
1. Create `backend/scrapers/[bank]_scraper.py`
2. Implement `fetch_[bank]_loan_data()` returning dict or None
3. Import in `backend/main.py` and add to the pipeline
4. Update `BANKS` list in relevant files (if hardcoded)
5. Run `python main.py` to test
6. Verify output in `data/loans_data.json`

### Updating Frontend UI
- Edit `frontend/index.html` for form fields or layout
- Update `frontend/js/app.js` to handle new fields (filtering, display)
- No rebuild needed; refresh browser to test

### Updating Loan Data Schema
1. Modify Pydantic models in `backend/utils.py`
2. Update scrapers to match new schema
3. Update `frontend/js/app.js` to display new fields
4. Regenerate `data/loans_data.json`

### Debugging Frontend
- Open browser DevTools (F12) → Console tab for errors
- Check Network tab to verify `loans_data.json` loaded correctly
- Verify HTTP server is running (file:// URLs break JSON loading)

---

## Data Schema

### loans_data.json Structure
```json
{
  "last_updated": "2024-01-15T12:00:00Z",
  "currency": "CZK",
  "banks": [
    {
      "id": "csas",
      "bank_name": "Česká spořitelna",
      "product_name": "Půjčka na cokoli",
      "logo_url": "assets/csas.png",
      "min_amount": 2000,
      "max_amount": 2500000,
      "min_duration_months": 6,
      "max_duration_months": 108,
      "interest_rate_from": 3.91,
      "rpsn_from": 4.03,
      "processing_fee": 0,
      "monthly_fee": 0,
      "web_url": "https://..."
    }
    // ... more banks
  ]
}
```

### BankLoanProduct Fields
- **id**, **bank_name**, **product_name**: Identifiers & display names
- **min/max_amount**: Loan range in CZK
- **min/max_duration_months**: Term range (typically 6-108 months)
- **interest_rate_from**, **rpsn_from**: Annual interest rates (%)
- **processing_fee**, **monthly_fee**: One-time & recurring fees (CZK)
- **web_url**: Bank's loan product page
- **logo_url**: Path to bank logo (typically `assets/[bank].png`)

---

## Pitfalls & Tips

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Frontend JSON fails to load | Serving over `file://` | Use HTTP server: `python -m http.server 8000` |
| Scraper returns None | Network error or HTML parse failure | Check User-Agent header, error logs in main.py |
| Calculator shows wrong monthly payment | Math error in formula | Verify annuity formula: `(1+r)^n` logic in calculator.js |
| New bank data not appearing | main.py not re-run | Run `python main.py` after adding/modifying scrapers |
| CSS changes not visible | Browser cache | Hard refresh (Ctrl+Shift+R) or clear cache |

### Tips for Adding Features
- **New filter field:** Add to form in `index.html`, handle in `app.js` filter logic
- **New bank:** Copy existing scraper template, update bank-specific selectors
- **Payment estimation:** Use `calculator.js` functions; don't duplicate math
- **Mobile UI:** Focus on `frontend/css/style.css` (currently empty—good candidate for improvement)

---

## Testing Notes

- **Backend:** Manually run `python main.py`, check `data/loans_data.json` for validity
- **Frontend:** Use browser DevTools; verify JSON loads in Network tab, check calculation accuracy
- **Scrapers:** Each should handle errors gracefully and log issues

---

## Next Steps for AI Agents

When working in this codebase:
1. **Understand the task scope:** Backend (scraping/data), Frontend (UI/UX), or both?
2. **Check data flow:** Which direction? Backend changes require re-running main.py
3. **Test after changes:** Backend: inspect JSON output. Frontend: refresh browser + DevTools
4. **Respect conventions:** Python naming, scraper pattern, Pydantic schema
5. **Coordinate frontend-backend:** Changes to data schema require updates in both layers
