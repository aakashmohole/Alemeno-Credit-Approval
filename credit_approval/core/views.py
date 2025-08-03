from django.shortcuts import render
from datetime import datetime
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import (
    CustomerRegisterSerializer, CustomerResponseSerializer,
    CheckEligibilitySerializer, CheckEligibilityResponseSerializer,
    CreateLoanSerializer, CreateLoanResponseSerializer,
    LoanWithCustomerSerializer, LoanDetailSerializer
)
from .utils import calculate_monthly_installment, calculate_credit_score
from django.shortcuts import get_object_or_404
from decimal import Decimal

from drf_yasg.utils import swagger_auto_schema

class RegisterCustomerAPIView(APIView):
    @swagger_auto_schema(
        request_body=CustomerRegisterSerializer,
        responses={201: CustomerResponseSerializer}
    )
    
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckEligibilityAPIView(APIView):
    
    @swagger_auto_schema(
        request_body=CheckEligibilitySerializer,
        responses={201: CheckEligibilityResponseSerializer}
    )
    
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer = get_object_or_404(Customer, customer_id=data['customer_id'])
        loans = Loan.objects.filter(customer=customer)

        credit_score = calculate_credit_score(customer, loans)

        # Filter active loans (end_date >= today)
        active_loans = loans.filter(end_date__gte=datetime.now().date())

        # Sum of current EMIs - convert Decimal to float for comparison
        sum_emis = sum([float(loan.monthly_payment) for loan in active_loans]) or 0.0
        monthly_salary = float(customer.monthly_salary)

        # Reject if total EMIs exceed 50% of monthly salary
        if sum_emis > monthly_salary * 0.5:
            approval = False
            corrected_interest_rate = float(data['interest_rate'])  # no correction here
        else:
            interest_rate = float(data['interest_rate'])
            approved = False
            corrected_interest_rate = interest_rate  # Initialize with requested interest rate

            # Eligibility and interest rate slab rules
            if credit_score > 50:
                approved = True
            elif 30 < credit_score <= 50:
                if interest_rate >= 12.0:
                    approved = True
                else:
                    approved = False
                    corrected_interest_rate = 12.0
            elif 10 < credit_score <= 30:
                if interest_rate >= 16.0:
                    approved = True
                else:
                    approved = False
                    corrected_interest_rate = 16.0
            else:  # credit_score <= 10
                approved = False

            # Check if sum of current loans exceeds approved_limit
            sum_current_loans = loans.filter(end_date__gte=datetime.now().date()).aggregate(
                total=models.Sum('loan_amount')
            )['total'] or Decimal(0)
            
            # Convert Decimal to float for comparison
            sum_current_loans_float = float(sum_current_loans)
            approved_limit_float = float(customer.approved_limit)

            if sum_current_loans_float > approved_limit_float:
                approved = False
                credit_score = 0

            approval = approved

        # Calculate EMI with the corrected_interest_rate
        emi = calculate_monthly_installment(
            float(data['loan_amount']),
            int(data['tenure']),
            corrected_interest_rate
        )
        
        response_data = {
            "customer_id": customer.customer_id,
            "approval": approval,
            "interest_rate": float(data['interest_rate']),
            "corrected_interest_rate": corrected_interest_rate,
            "tenure": data['tenure'],
            "monthly_installment": emi
        }

        return Response(response_data, status=status.HTTP_200_OK)

class CreateLoanAPIView(APIView):
    
    @swagger_auto_schema(
        request_body=CreateLoanSerializer,
        responses={201: CreateLoanResponseSerializer}
    )
        
    def post(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        customer = get_object_or_404(Customer, customer_id=data['customer_id'])
        loans = Loan.objects.filter(customer=customer)
        
        # Reuse eligibility check logic (simplified call)
        credit_score = calculate_credit_score(customer, loans)
        active_loans = loans.filter(end_date__gte=datetime.now().date())
        sum_emis = sum([loan.monthly_payment for loan in active_loans]) or Decimal(0)
        monthly_salary = customer.monthly_salary
        
        if sum_emis > monthly_salary * Decimal('0.5'):
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Total EMIs exceed 50% of monthly salary.",
                "monthly_installment": 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine interest rate slab (same logic as eligibility)
        interest_rate = data['interest_rate']
        approved = False
        corrected_interest_rate = interest_rate  # default
        
        if credit_score > 50:
            approved = True
        elif 30 < credit_score <= 50:
            if interest_rate >= 12.0:
                approved = True
            else:
                approved = False
                corrected_interest_rate = 12.0
        elif 10 < credit_score <= 30:
            if interest_rate >= 16.0:
                approved = True
            else:
                approved = False
                corrected_interest_rate = 16.0
        else:  # credit_score <= 10
            approved = False
        
        # Check sum of current loans
        sum_current_loans = active_loans.aggregate(total=models.Sum('loan_amount'))['total'] or 0
        if sum_current_loans + data['loan_amount'] > customer.approved_limit:
            approved = False

        emi = calculate_monthly_installment(
            data['loan_amount'], data['tenure'], corrected_interest_rate
        )
        
        if approved:
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=data['loan_amount'],
                tenure=data['tenure'],
                interest_rate=corrected_interest_rate,
                monthly_payment=emi
            )
            response_data = {
                "loan_id": loan.loan_id,
                "customer_id": customer.customer_id,
                "loan_approved": True,
                "message": "Loan approved successfully.",
                "monthly_installment": emi
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Loan not approved due to credit rating or limits.",
                "monthly_installment": emi
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class ViewLoanAPIView(APIView):
    
    @swagger_auto_schema(
        responses={201: LoanDetailSerializer}
    )
    
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        loan_data = {
            "loan_id": loan.loan_id,
            "customer": {
                "id": loan.customer.customer_id,
                "first_name": loan.customer.first_name,
                "last_name": loan.customer.last_name,
                "phone_number": loan.customer.phone_number,
                "age": loan.customer.age,
            },
            "loan_amount": float(loan.loan_amount),
            "interest_rate": loan.interest_rate,
            "monthly_installment": float(loan.monthly_payment),
            "tenure": loan.tenure,
        }
        return Response(loan_data, status=status.HTTP_200_OK)

class ViewLoansByCustomerAPIView(APIView):
    
    @swagger_auto_schema(
        responses={201: LoanWithCustomerSerializer}
    )
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)
        results = []
        for loan in loans:
            # Calculate repayments left roughly, as: tenure - EMIs paid on time
            repayments_left = max(0, loan.tenure - loan.emis_paid_on_time)
            results.append({
                "loan_id": loan.loan_id,
                "loan_amount": float(loan.loan_amount),
                "interest_rate": loan.interest_rate,
                "monthly_installment": float(loan.monthly_payment),
                "repayments_left": repayments_left
            })
        return Response(results, status=status.HTTP_200_OK)
