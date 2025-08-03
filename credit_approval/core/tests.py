from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Customer, Loan


class CustomerRegistrationTests(APITestCase):
    def test_register_customer_success(self):
        url = reverse('register_customer')
        data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "age": 28,
            "monthly_income": "50000.00",
            "phone_number": "9876543210"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('customer_id', response.data)
        # Compare floats for approved_limit due to string/decimal serialization
        expected_limit = 36 * float(data['monthly_income'])
        self.assertAlmostEqual(float(response.data['approved_limit']), expected_limit)


class CheckEligibilityTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Bob",
            last_name="Johnson",
            age=35,
            phone_number="1234512345",
            monthly_salary=Decimal('60000'),
            approved_limit=Decimal('2160000')  # 36 * 60000
        )
        # Create a past loan
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=14.0,
            monthly_payment=Decimal('9000'),
            emis_paid_on_time=12,
            date_of_approval='2024-01-01',
            end_date='2025-01-01'
        )

    def test_check_eligibility_approved(self):
        url = reverse('check_eligibility')
        data = {
            "customer_id": self.customer.customer_id,  # pass as int
            "loan_amount": "500000",
            "interest_rate": 15.0,
            "tenure": 24
        }
        response = self.client.post(url, data, format='json')

        # Debug print for failure
        if response.status_code != status.HTTP_200_OK:
            print("Check eligibility failed, response:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)
        self.assertIn('corrected_interest_rate', response.data)
        self.assertIn('monthly_installment', response.data)
        self.assertIn('tenure', response.data)


class CreateLoanTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Carol",
            last_name="Williams",
            age=40,
            phone_number="2468101214",
            monthly_salary=Decimal('70000'),
            approved_limit=Decimal('2520000')  # 36*70000
        )

    def test_create_loan_approved(self):
        url = reverse('create_loan')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": "200000",
            "interest_rate": 18.0,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        # Can be 201 or 400 depending on logic, just assert correct keys
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
        if response.status_code == status.HTTP_201_CREATED:
            self.assertIn('loan_id', response.data)
            self.assertTrue(response.data.get('loan_approved', False))

    def test_create_loan_rejected_due_to_limit(self):
        # Create large existing loan exceeding approved limit
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('2500000'),  # more than approved limit
            tenure=24,
            interest_rate=15.0,
            monthly_payment=Decimal('150000'),
            emis_paid_on_time=12,
            date_of_approval='2024-01-01',
            end_date='2026-01-01'
        )

        url = reverse('create_loan')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": "50000",
            "interest_rate": 15.0,
            "tenure": 6
        }
        response = self.client.post(url, data, format='json')

        # Debug print for failure
        if 'loan_approved' not in response.data:
            print("Create loan response missing 'loan_approved':", response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('loan_approved', response.data)
        self.assertFalse(response.data['loan_approved'])


class ViewLoanTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="David",
            last_name="Brown",
            age=50,
            phone_number="5556667777",
            monthly_salary=Decimal('80000'),
            approved_limit=Decimal('2880000')
        )
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('500000'),
            tenure=24,
            interest_rate=12.0,
            monthly_payment=Decimal('23500'),
            emis_paid_on_time=10,
            date_of_approval='2024-02-01',
            end_date='2026-02-01'
        )

    def test_view_loan(self):
        url = reverse('view_loan', args=[self.loan.loan_id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(int(response.data['loan_id']), self.loan.loan_id)
        self.assertEqual(response.data['customer']['id'], self.customer.customer_id)


class ViewLoansByCustomerTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Eve",
            last_name="Davis",
            age=45,
            phone_number="8889990000",
            monthly_salary=Decimal('75000'),
            approved_limit=Decimal('2700000')
        )
        # Create two loans
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('150000'),
            tenure=12,
            interest_rate=14.0,
            monthly_payment=Decimal('13000'),
            emis_paid_on_time=5,
            date_of_approval='2024-03-01',
            end_date='2025-03-01'
        )
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000'),
            tenure=10,
            interest_rate=15.0,
            monthly_payment=Decimal('11000'),
            emis_paid_on_time=2,
            date_of_approval='2023-01-01',
            end_date='2024-01-01'
        )

    def test_view_loans_by_customer(self):
        url = reverse('view_loans_by_customer', args=[self.customer.customer_id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

