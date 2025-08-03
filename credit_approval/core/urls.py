from django.urls import path
from .views import (
    RegisterCustomerAPIView, CheckEligibilityAPIView,
    CreateLoanAPIView, ViewLoanAPIView, ViewLoansByCustomerAPIView
)

urlpatterns = [
    path('register', RegisterCustomerAPIView.as_view(), name='register_customer'),
    path('check-eligibility', CheckEligibilityAPIView.as_view(), name='check_eligibility'),
    path('create-loan', CreateLoanAPIView.as_view(), name='create_loan'),
    path('view-loan/<int:loan_id>', ViewLoanAPIView.as_view(), name='view_loan'),
    path('view-loans/<int:customer_id>', ViewLoansByCustomerAPIView.as_view(), name='view_loans_by_customer'),
]
