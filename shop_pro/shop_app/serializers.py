from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']  # Add other fields here as needed
        extra_kwargs = {'password': {'write_only': True}}  # Ensure password is write-only

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class loginserializer(serializers.Serializer):
    username=serializers.CharField(max_length=30)
    password=serializers.CharField(max_length=30)


# class ShopSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Shop
#         fields = ['id', 'user', 'owner_name', 'address', 'contact_no', 'email']
    
class ShopSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Shop
        fields = ['id', 'username', 'owner_name', 'address', 'contact_no', 'email']

    def create(self, validated_data):
        # Retrieve the username from validated data
        username = validated_data.pop('username')

        # Retrieve the User object corresponding to the username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        # Create the Shop instance
        shop = Shop.objects.create(owner_name=validated_data['owner_name'],
                                   address=validated_data['address'],
                                   contact_no=validated_data['contact_no'],
                                   email=validated_data['email'])

        # Add the user to the shop's user set
        shop.user.add(user)

        return shop


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'pro_company', 'productname', 'quantity']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'shop', 'product_name', 'description', 'price', 'quantity_in_stock', 'stock']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class BillingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingDetails
        fields = ['id', 'customer_name', 'phone_number', 'email', 'billing_date', 'invoice_date', 'invoice_number', 'product_name', 'price', 'quantity', 'total_amount', 'coupon_code', 'payment_status', 'payment_method']
