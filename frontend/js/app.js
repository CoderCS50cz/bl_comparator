document.addEventListener('DOMContentLoaded', () => {
    const amountInput = document.getElementById('amount');
    const amountSlider = document.getElementById('amount-slider');
    const monthsInput = document.getElementById('months');
    const monthsSlider = document.getElementById('months-slider');
    const resultsDiv = document.getElementById('results');

    // Synchronizace posuvníků s číselnými poli
    function syncInputs(source, target) {
        target.value = source.value;
        loadAndCompare(); // Přepočítat při každé změně
    }

    amountInput.addEventListener('input', () => syncInputs(amountInput, amountSlider));
    amountSlider.addEventListener('input', () => syncInputs(amountSlider, amountInput));
    monthsInput.addEventListener('input', () => syncInputs(monthsInput, monthsSlider));
    monthsSlider.addEventListener('input', () => syncInputs(monthsSlider, monthsInput));

    async function loadAndCompare() {
        const amount = Number(amountInput.value);
        const months = Number(monthsInput.value);
        
        try {
            const response = await fetch(`../data/loans_data.json?nocache=${new Date().getTime()}`);
            const data = await response.json();
            
            resultsDiv.innerHTML = ''; 
            
            const validOffers = data.banks.filter(bank => 
                amount >= bank.min_amount && amount <= bank.max_amount && 
                months >= bank.min_duration_months && months <= bank.max_duration_months
            );

            if (validOffers.length === 0) {
                resultsDiv.innerHTML = '<div class="card"><p>Pro zadané parametry bohužel neexistuje žádná nabídka.</p></div>';
                return;
            }

            const results = validOffers.map(bank => {
                const monthlyPayment = calculateAnnuity(amount, bank.interest_rate_from, months);
                return { ...bank, monthlyPayment, totalPaid: monthlyPayment * months };
            });

            results.sort((a, b) => a.monthlyPayment - b.monthlyPayment);

            results.forEach(offer => {
                resultsDiv.innerHTML += `
                    <div class="bank-card">
                        <h3>${offer.bank_name}</h3>
                        <div class="result-row">
                            <span>Úroková sazba od</span>
                            <strong>${offer.interest_rate_from} %</strong>
                        </div>
                        <div class="result-row">
                            <span>RPSN od</span>
                            <strong>${offer.rpsn_from} %</strong>
                        </div>
                        <div class="payment-row">
                            <span>Měsíční splátka</span>
                            <strong>${offer.monthlyPayment.toLocaleString('cs-CZ')} Kč</strong>
                        </div>
                        <div class="result-row" style="border-top: 1px solid #eef2f0; padding-top: 12px;">
                            <span>Celkem zaplatíte</span>
                            <strong>${offer.totalPaid.toLocaleString('cs-CZ')} Kč</strong>
                        </div>
                        <a href="${offer.web_url}" target="_blank" class="btn-apply">Přejít na web banky</a>
                    </div>
                `;
            });

        } catch (error) {
            resultsDiv.innerHTML = '<div class="card"><p style="color: red;">Chyba při načítání dat z backendu.</p></div>';
        }
    }

    // Prvotní načtení
    loadAndCompare();
});