let banksData = [];

document.addEventListener('DOMContentLoaded', () => {
    fetch('data/loans_data.json')
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data)) {
                banksData = data;
            } else if (data.banks && Array.isArray(data.banks)) {
                banksData = data.banks;
            } else if (data.data && Array.isArray(data.data)) {
                banksData = data.data;
            } else {
                banksData = Object.values(data).filter(item => 
                    item !== null && typeof item === 'object' && !Array.isArray(item) && (item.id || item.bank_name)
                );
            }
            renderBanks(banksData); 
            triggerUpdate(); 
        })
        .catch(error => console.error("Chyba při načítání dat:", error));
});

function renderBanks(data) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; 

    data.forEach(bank => {
        let rateRowHTML = `
            <div class="detail-row">
                <span>Úroková sazba od</span>
                <strong><span class="interest-rate-value">${bank.interest_rate_from}</span> %</strong>
            </div>
        `;

        // SPECIFICKÁ ÚPRAVA PRO AIR BANK - Rozbalovací seznam přímo v detail-row
        if (bank.id === 'airbank' && bank.rate_card && bank.rate_card.length > 0) {
            const uniqueRates = [...new Set(bank.rate_card.map(r => r.interest_rate))].sort((a,b) => a-b);
            let options = uniqueRates.map(rate => `<option value="${rate}">${rate} %</option>`).join('');
            
            rateRowHTML = `
                <div class="detail-row" style="align-items: center;">
                    <span>Zvolená úroková sazba</span>
                    <select id="airbank-rate-select" onchange="triggerUpdate()" style="border: 1px solid #008a55; border-radius: 4px; padding: 2px 4px; font-weight: 700; font-family: inherit; font-size: 0.95rem; color: #008a55; background: #f4f7f6; cursor: pointer; outline: none; text-align: right;">
                        ${options}
                    </select>
                </div>
            `;
        }

        const cardHTML = `
            <div class="bank-card" id="bank-${bank.id}">
                <div class="bank-header">
                    <h3>${bank.bank_name}</h3>
                </div>
                <div class="bank-details">
                    ${rateRowHTML}
                    <div class="detail-row">
                        <span>RPSN od</span>
                        <strong><span class="rpsn-value">${bank.rpsn_from}</span> %</strong>
                    </div>
                    
                    <div class="payment-highlight">
                        <span class="payment-label">Měsíční splátka</span>
                        <div class="payment-amount"><span class="monthly-payment-value">0</span> Kč</div>
                    </div>
                    
                    <div class="detail-row total-amount-row">
                        <span>Celkem zaplatíte</span>
                        <strong><span class="total-payment-value">0</span> Kč</strong>
                    </div>

                    <a href="${bank.web_url}" target="_blank" class="btn-primary">Přejít na web banky</a>
                </div>
            </div>
        `;
        resultsContainer.innerHTML += cardHTML;
    });
}

// --- LOGIKA PRO POSUVNÍKY A POLÍČKA ---
const amountInput = document.getElementById('amount');
const amountSlider = document.getElementById('amount-slider');
const monthsInput = document.getElementById('months');
const monthsSlider = document.getElementById('months-slider');

amountInput.step = "10000";

const allowedAmounts = [20000];
for (let i = 50000; i <= 2500000; i += 50000) {
    allowedAmounts.push(i);
}

function getClosestAmount(val) {
    return allowedAmounts.reduce((prev, curr) => Math.abs(curr - val) < Math.abs(prev - val) ? curr : prev);
}

let lastAmount = parseInt(amountInput.value) || 150000;

amountSlider.addEventListener('input', (e) => {
    const val = getClosestAmount(parseInt(e.target.value) || 20000);
    amountSlider.value = val;
    amountInput.value = val;
    lastAmount = val;
    triggerUpdate();
});

amountInput.addEventListener('input', (e) => {
    let val = parseInt(e.target.value);
    if (isNaN(val)) return; 

    let diff = val - lastAmount;

    if (diff === 10000 || diff === -10000) {
        if (diff > 0) { 
            const currentIndex = allowedAmounts.findIndex(a => a >= lastAmount);
            val = allowedAmounts[currentIndex] === lastAmount ? allowedAmounts[currentIndex + 1] : allowedAmounts[currentIndex];
            if (val === undefined) val = allowedAmounts[allowedAmounts.length - 1]; 
        } else { 
            let prevVals = allowedAmounts.filter(a => a < lastAmount);
            val = prevVals.length > 0 ? prevVals[prevVals.length - 1] : allowedAmounts[0];
        }
        amountInput.value = val;
    } 

    lastAmount = val;
    amountSlider.value = getClosestAmount(val); 
    triggerUpdate(); 
});

amountInput.addEventListener('change', (e) => {
    let val = parseInt(e.target.value) || 20000;
    val = Math.max(20000, Math.min(2500000, val));
    amountInput.value = val;
    lastAmount = val;
    amountSlider.value = getClosestAmount(val);
    triggerUpdate();
});

monthsSlider.addEventListener('input', (e) => {
    let val = Math.max(6, Math.min(120, Math.round(parseInt(e.target.value) / 3) * 3));
    monthsSlider.value = val;
    monthsInput.value = val;
    triggerUpdate();
});

monthsInput.addEventListener('input', (e) => {
    let val = parseInt(e.target.value);
    if (isNaN(val)) return;
    monthsSlider.value = Math.max(6, Math.min(120, Math.round(val / 3) * 3));
    triggerUpdate();
});

monthsInput.addEventListener('change', (e) => {
    let val = parseInt(e.target.value) || 48;
    val = Math.max(6, Math.min(120, val));
    monthsInput.value = val;
    monthsSlider.value = Math.max(6, Math.min(120, Math.round(val / 3) * 3));
    triggerUpdate();
});

function triggerUpdate() {
    const amount = parseInt(amountInput.value) || 20000;
    const months = parseInt(monthsInput.value) || 48;
    
    if (banksData.length > 0 && typeof updateBankCardsUI === "function") {
        updateBankCardsUI(amount, months, banksData);
    }
}