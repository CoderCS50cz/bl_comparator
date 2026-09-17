/**
 * Výpočet anuitní splátky
 * @param {number} principal - Výše úvěru (jistina)
 * @param {number} annualRate - Roční úroková sazba v procentech
 * @param {number} months - Doba splácení v měsících
 * @returns {number} - Zaokrouhlená měsíční splátka
 */
function calculateAnnuity(principal, annualRate, months) {
    if (annualRate === 0) return Math.round(principal / months);
    
    // Převod p.a. sazby na měsíční úrokovou míru (desetinné číslo)
    const monthlyRate = (annualRate / 100) / 12;
    
    // Anuitní vzorec
    const numerator = monthlyRate * Math.pow(1 + monthlyRate, months);
    const denominator = Math.pow(1 + monthlyRate, months) - 1;
    
    return Math.round(principal * (numerator / denominator));
}