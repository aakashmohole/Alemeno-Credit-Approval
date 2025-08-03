from django.db import models

class Customer(models.Model):
    customer_id = models.CharField(max_length=20,  primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(null=True, blank=True)  # Added Age
    phone_number = models.CharField(max_length=20)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)
    # current_debt field removed as it does not appear in updated columns

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_id = models.CharField(max_length=20, primary_key=True)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)  # renamed to match your column
    emis_paid_on_time = models.IntegerField()
    date_of_approval = models.DateField()  # renamed to match your column
    end_date = models.DateField()
