from django.shortcuts import render
from datetime import datetime, date
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import (
    CustomerRegisterSerializer, CustomerResponseSerializer,
    CheckEligibilitySerializer, CheckEligibilityResponseSerializer,
    CreateLoanSerializer, CreateLoanResponseSerializer,
    LoanDetailSerializer, ViewLoansByCustomerSerializer
)
from .utils import calculate_monthly_installment, calculate_credit_score
from django.shortcuts import get_object_or_404
from decimal import Decimal
from dateutil.relativedelta import relativedelta

class RegisterCustomerAPIView(APIView):
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckEligibilityAPIView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer = get_object_or_404(Customer, customer_id=data['customer_id'])
        loans = Loan.objects.filter(customer=customer)

        eligibility = self.get_eligibility(customer, loans, data['loan_amount'], data['interest_rate'], data['tenure'])
        
        response_data = {
            "customer_id": data['customer_id'],
            "approval": eligibility['approval'],
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": eligibility['corrected_interest_rate'],
            "tenure": data['tenure'],
            "monthly_installment": eligibility['monthly_installment']
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def get_eligibility(self, customer, loans, loan_amount, interest_rate, tenure):
        credit_score = calculate_credit_score(customer, loans)
        active_loans = loans.filter(end_date__gte=date.today())
        
        # Rule: sum of all current EMIs > 50% of monthly salary
        sum_emis = active_loans.aggregate(total=models.Sum('monthly_payment'))['total'] or Decimal(0)
        if sum_emis > customer.monthly_salary * Decimal('0.5'):
            return {
                "approval": False,
                "corrected_interest_rate": interest_rate,
                "monthly_installment": 0
            }

        approved = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approved = True
        elif 50 > credit_score > 30:
            if interest_rate < 12:
                corrected_interest_rate = 12.0
            approved = True
        elif 30 > credit_score > 10:
            if interest_rate < 16:
                corrected_interest_rate = 16.0
            approved = True
        else: # score < 10
            approved = False

        # Rule: if sum of current loans > approved limit, score = 0 (handled in utility, but double check volume)
        sum_current_loans = active_loans.aggregate(total=models.Sum('loan_amount'))['total'] or Decimal(0)
        if sum_current_loans + Decimal(str(loan_amount)) > customer.approved_limit:
            approved = False

        emi = calculate_monthly_installment(float(loan_amount), int(tenure), float(corrected_interest_rate))
        
        return {
            "approval": approved,
            "corrected_interest_rate": corrected_interest_rate,
            "monthly_installment": emi
        }

class CreateLoanAPIView(CheckEligibilityAPIView):
    def post(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        customer = get_object_or_404(Customer, customer_id=data['customer_id'])
        loans = Loan.objects.filter(customer=customer)
        
        eligibility = self.get_eligibility(customer, loans, data['loan_amount'], data['interest_rate'], data['tenure'])
        
        if eligibility['approval']:
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=Decimal(str(data['loan_amount'])),
                tenure=data['tenure'],
                interest_rate=eligibility['corrected_interest_rate'],
                monthly_payment=Decimal(str(eligibility['monthly_installment'])),
                date_of_approval=date.today(),
                end_date=date.today() + relativedelta(months=data['tenure'])
            )
            return Response({
                "loan_id": loan.loan_id,
                "customer_id": customer.customer_id,
                "loan_approved": True,
                "message": "Loan approved successfully.",
                "monthly_installment": eligibility['monthly_installment']
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Loan not approved based on eligibility criteria.",
                "monthly_installment": eligibility['monthly_installment']
            }, status=status.HTTP_400_BAD_REQUEST)

class ViewLoanAPIView(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ViewLoansByCustomerAPIView(APIView):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)
        serializer = ViewLoansByCustomerSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
