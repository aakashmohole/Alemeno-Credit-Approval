import pandas as pd
from celery import shared_task
from django.db import transaction
from core.models import Customer, Loan
from decimal import Decimal
from datetime import datetime

@shared_task
def ingest_initial_data_task():
    # Helper to parse date from various formats
    def parse_date(date_val):
        if pd.isna(date_val):
            return None
        if isinstance(date_val, datetime):
            return date_val.date()
        try:
            return pd.to_datetime(date_val).date()
        except:
            return None

    # Load data
    try:
        customers_df = pd.read_excel('customer_data.xlsx')
        loans_df = pd.read_excel('loan_data.xlsx')
    except Exception as e:
        return f"Error loading Excel files: {str(e)}"

    customers_created = 0
    loans_created = 0

    with transaction.atomic():
        # Customer data ingestion
        for _, row in customers_df.iterrows():
            customer_id = str(row['Customer ID']).strip()
            if not customer_id or customer_id == 'nan':
                continue
            
            Customer.objects.update_or_create(
                customer_id=customer_id,
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'age': row.get('Age') if not pd.isna(row.get('Age')) else None,
                    'phone_number': str(row['Phone Number']),
                    'monthly_salary': Decimal(str(row['Monthly Salary'])),
                    'approved_limit': Decimal(str(row['Approved Limit'])),
                }
            )
            customers_created += 1

        # Loan data ingestion
        for _, row in loans_df.iterrows():
            loan_id = str(row['Loan ID']).strip()
            customer_id = str(row['Customer ID']).strip()
            
            if not loan_id or loan_id == 'nan' or not customer_id or customer_id == 'nan':
                continue

            try:
                customer = Customer.objects.get(customer_id=customer_id)
                Loan.objects.update_or_create(
                    loan_id=loan_id,
                    defaults={
                        'customer': customer,
                        'loan_amount': Decimal(str(row['Loan Amount'])),
                        'tenure': int(row['Tenure']),
                        'interest_rate': float(row['Interest Rate']),
                        'monthly_payment': Decimal(str(row['Monthly payment'])),
                        'emis_paid_on_time': int(row['EMIs paid on Time']),
                        'date_of_approval': parse_date(row['Date of Approval']),
                        'end_date': parse_date(row['End Date']),
                    }
                )
                loans_created += 1
            except Customer.DoesNotExist:
                continue

    return f"Ingestion successful: {customers_created} customers, {loans_created} loans."
