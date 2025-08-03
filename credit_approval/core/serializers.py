from rest_framework import serializers
from .models import Customer, Loan

class CustomerRegisterSerializer(serializers.ModelSerializer):
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, source='monthly_salary')
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'phone_number', 'monthly_income']
    
    def create(self, validated_data):
        monthly_salary = validated_data['monthly_salary']
        approved_limit = round(36 * monthly_salary, -5)  # nearest lakh rounding
        validated_data['approved_limit'] = approved_limit
        return Customer.objects.create(**validated_data)

class CustomerResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, source='monthly_salary')
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField(min_value=1)

class CheckEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=15, decimal_places=2)

class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField(min_value=1)

class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=15, decimal_places=2)

class LoanDetailSerializer(serializers.ModelSerializer):
    monthly_installment = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']

class LoanWithCustomerSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = serializers.FloatField()
    monthly_installment = serializers.DecimalField(max_digits=15, decimal_places=2)
    tenure = serializers.IntegerField()
    customer = serializers.SerializerMethodField()

    def get_customer(self, obj):
        c = obj.customer
        return {
            "id": c.customer_id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "phone_number": c.phone_number,
            "age": c.age,
        }
