function calculateAnnuity(principal, annualRate, months) {
    if (annualRate === 0) return Math.round(principal / months);
    const monthlyRate = (annualRate / 100) / 12;
    const payment = principal * (monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);
    return Math.round(payment);
}