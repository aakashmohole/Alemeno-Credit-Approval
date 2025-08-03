from django.db import models
from datetime import datetime
import math

def calculate_monthly_installment(principal, tenure_in_months, annual_interest_rate):
    """
    EMI calculation using compound interest formula:
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)

    Where:
    P = principal loan amount
    r = monthly interest rate (annual_interest_rate/12/100)
    n = tenure in months
    """
    if annual_interest_rate == 0:
        return principal / tenure_in_months
    
    r = annual_interest_rate / 12 / 100
    n = tenure_in_months
    emi = principal * r * (1 + r)**n / ((1 + r)**n - 1)
    return round(emi, 2)

def calculate_credit_score(customer, loans_queryset):
    """
    Calculate credit score based on:
    i. Past loans paid on time
    ii. Number of loans taken
    iii. Loan activity current year
    iv. Loan approved volume
    v. > approved_limit condition results in 0
    
    Returns an int score between 0-100.
    """
    # Sum of current loans (active loans)
    sum_current_loans = loans_queryset.filter(end_date__gte=datetime.now().date()).aggregate(
        total=models.Sum('loan_amount')
    )['total'] or 0
    
    if sum_current_loans > customer.approved_limit:
        return 0
    
    # Number of loans taken (count)
    num_loans = loans_queryset.count()
    
    # Count loans paid on time ratio (%)
    total_emis = loans_queryset.aggregate(total=models.Sum('tenure'))['total'] or 1
    total_onschedule_emis = loans_queryset.aggregate(
        total_on_time=models.Sum('emis_paid_on_time'))['total_on_time'] or 0
    paid_on_time_ratio = (total_onschedule_emis / total_emis) if total_emis > 0 else 0
    
    # Loan activity current year - count loans approved in current year
    current_year = datetime.now().year
    current_year_loans = loans_queryset.filter(date_of_approval__year=current_year).count()
    
    # Loan approved volume: sum of loan_amounts
    approved_volume = loans_queryset.aggregate(total=models.Sum('loan_amount'))['total'] or 0
    
    # Assign weights to different components (customizable)
    score = 0
    score += min(30, paid_on_time_ratio * 30)  # max 30 points
    score += min(20, max(0, 20 - num_loans))    # fewer loans better, max 20
    score += min(20, current_year_loans * 4)   # more activity up to 20
    approved_volume_float = float(approved_volume)
    approved_limit_float = float(customer.approved_limit)

    score += min(30, max(0, 30 - (approved_volume_float / approved_limit_float) * 30))  # volume penalty

    
    return int(min(100, score))
