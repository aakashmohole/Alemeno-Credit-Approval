import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Customer, Loan


class Command(BaseCommand):
    help = 'Injects customer and loan data from Excel files'

    def handle(self, *args, **kwargs):
        # Read Excel files
        customers = pd.read_excel('customer_data.xlsx')
        loans = pd.read_excel('loan_data.xlsx')

        # Customer data insertion
        for _, row in customers.iterrows():
            # Clean and convert data as needed
            # customer_id = row['Customer ID']
            customer_id = str(row['Customer ID']).strip()
            if pd.isna(customer_id) or customer_id == "":
                continue
                self.stdout.write(self.style.WARNING('Skipping customer row with empty Customer ID'))
            first_name = row['First Name']
            last_name = row['Last Name']
            age = row.get('Age')
            if pd.isna(age):
                age = None
            phone_number = row['Phone Number']
            monthly_salary = row['Monthly Salary']
            approved_limit = row['Approved Limit']

            Customer.objects.update_or_create(
                customer_id=int(customer_id),  # ensure int type if your model uses IntegerField or AutoField
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'age': age,
                    'phone_number': phone_number,
                    'monthly_salary': monthly_salary,
                    'approved_limit': approved_limit,
                }
            )

        # Loan data insertion
        for _, row in loans.iterrows():
            # customer_id = row['Customer ID']
            # loan_id = row['Loan ID']
            customer_id = str(row['Customer ID']).strip()
            loan_id = str(row['Loan ID']).strip()

            if pd.isna(customer_id) or customer_id == "":
                continue
                self.stdout.write(self.style.WARNING('Skipping loan row with empty Customer ID'))
            if pd.isna(loan_id) or loan_id == "":
                continue
                self.stdout.write(self.style.WARNING('Skipping loan row with empty Loan ID'))

            try:
                customer = Customer.objects.get(customer_id=int(customer_id))
            except Customer.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Customer with ID {customer_id} not found for loan"))
                continue

            loan_amount = row['Loan Amount']
            tenure = row['Tenure']
            interest_rate = row['Interest Rate']
            monthly_payment = row['Monthly payment']
            emis_paid_on_time = row['EMIs paid on Time']
            date_of_approval = row['Date of Approval']
            end_date = row['End Date']

            # Convert NaN dates to None if necessary
            if pd.isna(date_of_approval):
                date_of_approval = None
            if pd.isna(end_date):
                end_date = None

            Loan.objects.update_or_create(
                loan_id=int(loan_id),
                defaults={
                    'customer': customer,
                    'loan_amount': loan_amount,
                    'tenure': tenure,
                    'interest_rate': interest_rate,
                    'monthly_payment': monthly_payment,
                    'emis_paid_on_time': emis_paid_on_time,
                    'date_of_approval': date_of_approval,
                    'end_date': end_date,
                }
            )
        self.stdout.write(self.style.SUCCESS('Data injection completed successfully.'))
