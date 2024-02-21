from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from .models import Shop
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from .serializers import *
from .serializers import CustomUserSerializer, loginserializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.shortcuts import get_object_or_404

class AdminRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': "Registered successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        qs = User.objects.all()
        serializer = CustomUserSerializer(qs, many=True)
        return Response(serializer.data)

class AdminLoginView(APIView):
    def post(self, request):
        serializer = loginserializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")
            
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                # Generate or retrieve the token for the user
                token, created = Token.objects.get_or_create(user=user)
                return Response({'msg': 'logged in successfully', 'token': token.key})
            else:
                return Response({'msg': 'login failed'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ShopListCreateAPIView(generics.ListCreateAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response_data = {
                'message': 'Shop added successfully',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'message': 'Shops retrieved successfully',
            'data': serializer.data,
            'username': request.user.username 
        }
        return Response(response_data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
            response_data = {
                'message': 'Shop updated successfully',
                'data': serializer.data
            }
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Shop deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class ProductAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            # Check if the shop associated with the product is the logged-in shop
            if request.user == serializer.validated_data['shop'].user:
                # Check if the stock_id is provided in the request data
                if 'stock' in request.data:
                    serializer.save()
                    return Response({'message': 'Product successfully added'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Stock is required'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'You are not authorized to add products for this shop'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user == product.shop.user:
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'You are not authorized to update this product'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user == product.shop.user:
            product.delete()
            return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'You are not authorized to delete this product'}, status=status.HTTP_403_FORBIDDEN)
        

class EmployeeAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure that only the shop associated with the employee can add them
            if request.user.shop.id == serializer.validated_data['shop'].id:
                serializer.save()
                return Response({'message': 'Employee successfully added'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'You are not authorized to add employees for this shop'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request):
        employee = Employee.objects.all()
        serializer = EmployeeSerializer(employee,many=True)
        return Response(serializer.data)
    

    def put(self, request, pk):
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            # Ensure that only the shop associated with the employee can update them
            if request.user.shop.id == serializer.validated_data['shop'].id:
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({'error': 'You are not authorized to update employees for this shop'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        employee = self.get_object(pk)
        # Ensure that only the shop associated with the employee can delete them
        if request.user.shop.id == employee.shop.id:
            employee.delete()
            return Response({'message': 'Employee successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'You are not authorized to delete employees for this shop'}, status=status.HTTP_403_FORBIDDEN)
        



class StockListCreateAPIView(APIView):
    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Stock created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk)
        except Stock.DoesNotExist:
            return None

    def get(self, request, pk):
        stock = self.get_object(pk)
        if stock:
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        return Response({'error': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        stock = self.get_object(pk)
        if stock:
            serializer = StockSerializer(stock, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Stock updated successfully'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        stock = self.get_object(pk)
        if stock:
            stock.delete()
            return Response({'message': 'Stock deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Stock not found'}, status=status.HTTP_404_NOT_FOUND)
    

from django.db.models import Sum  # Import Sum function from Django

class BillingDetailsView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve product names and quantities from the request data
            product_names = request.data.get('product_name').split(',')
            quantities = [int(quantity) for quantity in request.data.get('quantity').split(',')]
            
            # Initialize variables to store total amount and billing details list
            total_amount = 0
            billing_details_list = []

            # Iterate over product names and quantities
            for product_name, quantity in zip(product_names, quantities):
                # Retrieve the product based on the provided product_name
                product = Product.objects.get(product_name=product_name)

                # Calculate the total amount for this item
                item_total_amount = product.price * quantity

                # Apply coupon code discount if available
                coupon_code = request.data.get('coupon_code')
                if coupon_code:
                    # Assuming a fixed discount amount for the coupon code
                    coupon_discount = 10  # Example: Fixed discount of 10 units
                    item_total_amount -= coupon_discount

                # Update the total amount with the current item's total amount
                total_amount += item_total_amount

                # Create BillingDetails instance with populated fields
                billing_details = BillingDetails(
                    customer_name=request.data.get('customer_name'),
                    phone_number=request.data.get('phone_number'),
                    email=request.data.get('email'),
                    invoice_number=request.data.get('invoice_number'),
                    product_name=product_name,
                    price=product.price,
                    quantity=quantity,
                    total_amount=item_total_amount,  # Use the total amount for this item
                    coupon_code=coupon_code,
                    payment_status=request.data.get('payment_status'),
                    payment_method=request.data.get('payment_method')
                )
                billing_details.save()

                # Append billing details to the list
                billing_details_list.append({
                    'id': billing_details.id,
                    'customer_name': billing_details.customer_name,
                    'phone_number': billing_details.phone_number,
                    'email': billing_details.email,
                    'invoice_number': billing_details.invoice_number,
                    'product_name': billing_details.product_name,
                    'price': billing_details.price,
                    'quantity': billing_details.quantity,
                    'total_amount': billing_details.total_amount,
                    'coupon_code': billing_details.coupon_code,
                    'payment_status': billing_details.payment_status,
                    'payment_method': billing_details.payment_method
                })

            # Return response with total amount and billing details list
            return Response({
                'message': 'Billing details saved successfully.',
                'total_amount': total_amount,
                'billing_details': billing_details_list,
                'grand_total': total_amount  # Return the total amount as grand total
            }, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, customer_name, *args, **kwargs):
        try:
            # Filter BillingDetails queryset based on the customer name
            billing_details_queryset = BillingDetails.objects.filter(customer_name=customer_name)

            # Serialize the billing details queryset
            serializer = BillingDetailsSerializer(billing_details_queryset, many=True)

            # Calculate total amount for the user
            total_amount = billing_details_queryset.aggregate(total_amount=Sum('total_amount'))['total_amount']

            # Return serialized billing details and total amount in the response
            return Response({
                'message': f'Full details of billing retrieved successfully for {customer_name}.',
                'total_amount': total_amount if total_amount else 0,  # Set total amount to 0 if no records are found
                'billing_details': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self, request, pk, *args, **kwargs):
        try:
            # Retrieve the billing detail object to update
            billing_detail = BillingDetails.objects.get(pk=pk)

            # Deserialize the request data and update the billing detail object
            serializer = BillingDetailsSerializer(billing_detail, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Billing details updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BillingDetails.DoesNotExist:
            return Response({'error': 'Billing detail not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)