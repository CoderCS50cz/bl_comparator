document.getElementById('calculate').addEventListener('click', async () => {
    const amount = Number(document.getElementById('amount').value);
    const months = Number(document.getElementById('months').value);
    const resultsDiv = document.getElementById('results');
    
    try {
        const res = await fetch('../data/loans_data.json');
        const data = await res.json();
        
        resultsDiv.innerHTML = ''; // Vyčištění starých výsledků
        
        data.banks.forEach(bank => {
            // Zobrazení nabídky pouze pokud vstup spadá do limitů dané banky
            if (amount >= bank.min_amount && amount <= bank.max_amount && months >= bank.min_duration_months && months <= bank.max_duration_months) {
                const monthlyPayment = calculateAnnuity(amount, bank.interest_rate_from, months);
                const totalPaid = monthlyPayment * months;
                
                resultsDiv.innerHTML += `
                    <div class="card">
                        <h3>${bank.bank_name} - ${bank.product_name}</h3>
                        <p>Úroková sazba od: <strong>${bank.interest_rate_from} % p.a.</strong></p>
                        <p>Měsíční splátka: <strong>${monthlyPayment} Kč</strong></p>
                        <p>Celkem zaplatíte: <strong>${totalPaid} Kč</strong></p>
                    </div><hr>`;
            }
        });
    } catch (error) {
        resultsDiv.innerHTML = '<p>Chyba při načítání dat. Ujistěte se, že používáte lokální server.</p>';
    }
});