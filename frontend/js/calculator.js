function calculateAnnuity(principal, annualRate, months) {
    if (annualRate === 0) return principal / months;
    
    const monthlyRate = annualRate / 100 / 12;
    const annuity = principal * (monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);
    
    return Math.round(annuity);
}

function findApplicableRate(rateCard, targetAmount, targetMonths) {
    if (!rateCard || rateCard.length === 0) return null;
    
    let bestMatch = null;
    
    for (const rateObj of rateCard) {
        if (targetAmount <= rateObj.amount && targetMonths <= rateObj.months) {
            if (!bestMatch) {
                bestMatch = rateObj;
            } else {
                const amountDiff = rateObj.amount - targetAmount;
                const monthsDiff = rateObj.months - targetMonths;
                
                const currentBestAmountDiff = bestMatch.amount - targetAmount;
                const currentBestMonthsDiff = bestMatch.months - targetMonths;
                
                if (amountDiff <= currentBestAmountDiff && monthsDiff <= currentBestMonthsDiff) {
                    bestMatch = rateObj;
                }
            }
        }
    }
    
    if (!bestMatch) {
        bestMatch = rateCard[rateCard.length - 1];
    }
    
    return bestMatch;
}

function updateBankCardsUI(selectedAmount, selectedMonths, banksData) {
    banksData.forEach(bank => {
        const bankCard = document.getElementById(`bank-${bank.id}`);
        if (!bankCard) return;

        // DYNAMICKÉ FILTROVÁNÍ: Skrytí karet, které nesplňují limity banky
        if (selectedAmount < bank.min_amount || 
            selectedAmount > bank.max_amount || 
            selectedMonths < bank.min_duration_months || 
            selectedMonths > bank.max_duration_months) {
            
            bankCard.style.display = 'none'; 
            return; 
        } else {
            bankCard.style.display = 'flex'; 
        }

        let currentInterestRate = bank.interest_rate_from;
        let currentRpsn = bank.rpsn_from;

        // LOGIKA PRO AIR BANK: Sazba se čte z uživatelského rozbalovacího menu
        if (bank.id === 'airbank') {
            const selectEl = document.getElementById('airbank-rate-select');
            if (selectEl) {
                currentInterestRate = parseFloat(selectEl.value);
                const matchedRate = bank.rate_card.find(r => r.interest_rate === currentInterestRate);
                if (matchedRate) {
                    currentRpsn = matchedRate.rpsn;
                }
            }
        } 
        // LOGIKA PRO VŠECHNY OSTATNÍ BANKY: Hledáme podle částky a měsíců
        else {
            const dynamicRate = findApplicableRate(bank.rate_card, selectedAmount, selectedMonths);
            if (dynamicRate) {
                currentInterestRate = dynamicRate.interest_rate;
                currentRpsn = dynamicRate.rpsn;
            }
            
            // Text sazby přepisujeme jen tam, kde není <select>
            const rateElement = bankCard.querySelector('.interest-rate-value');
            if (rateElement) rateElement.textContent = currentInterestRate.toFixed(2);
        }

        const monthlyPayment = calculateAnnuity(selectedAmount, currentInterestRate, selectedMonths);
        const totalPayment = monthlyPayment * selectedMonths;

        // Přepis RPSN, měsíční splátky a celkové splátky
        const rpsnElement = bankCard.querySelector('.rpsn-value');
        if (rpsnElement) rpsnElement.textContent = currentRpsn.toFixed(2);

        const paymentElement = bankCard.querySelector('.monthly-payment-value');
        if (paymentElement) paymentElement.textContent = monthlyPayment.toLocaleString('cs-CZ');
        
        const totalElement = bankCard.querySelector('.total-payment-value');
        if (totalElement) totalElement.textContent = totalPayment.toLocaleString('cs-CZ');
    });
}