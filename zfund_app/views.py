from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import User, Product, Category, Purchase
from .serializers import UserSerializer, CategorySerializer, ProductSerializer, PurchaseSerializer
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
import pyotp
from rest_framework_simplejwt.tokens import RefreshToken
from zfunds_app.settings import SIMPLE_JWT
from rest_framework.views import APIView

class AdvisorSignUp(APIView):
    def post(request):
        if request.method == 'POST':
            mobile_number = request.data.get('mobile_number')
            otp_input = request.data.get('otp')

            if not mobile_number or not otp_input:
                return Response({'error': 'Mobile number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(mobile_number=mobile_number)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Generate and verify OTP
            otp_secret = user.mobile_number
            totp = pyotp.TOTP(otp_secret)
            is_valid_otp = totp.verify(otp_input)

            if not is_valid_otp:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            if user.role != 'advisor':
                user.role = 'advisor'  # Set the user's role to advisor
                user.save()

            # Issue a token using django-rest-framework-simplejwt
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

        return Response({'message': 'Advisor account created successfully.', 'token': token}, status=status.HTTP_201_CREATED)

@permission_classes(['IsAuthenticated'])     
class AddClient(APIView):
    def post(request):
        if request.method == 'POST':
            advisor = request.user  # Assuming the advisor is the authenticated user

            client_name = request.data.get('client_name')
            client_mobile = request.data.get('client_mobile')

            if not client_name or not client_mobile:
                return Response({'error': 'Client name and mobile number are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the client user with the role 'user' and associate it with the advisor
            client_user = User.objects.create(
                mobile_number=client_mobile,
                role='user',
                advisor=advisor  # Assuming you have a ForeignKey field in the User model to associate users with advisors
            )

            serializer = UserSerializer(client_user)

            return Response({'message': 'Client added successfully.', 'client_details': serializer.data}, status=status.HTTP_201_CREATED)


@permission_classes(['IsAuthenticated']) 
class ListClients(APIView):
    def get(request, advisor_id):
        if request.method == 'GET':
            try:
                advisor = User.objects.get(id=advisor_id, role='advisor')  # Assuming 'advisor' is the role for advisors
            except User.DoesNotExist:
                return Response({'error': 'Advisor not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve all clients associated with this advisor
            clients = User.objects.filter(advisor=advisor, role='user')  # Assuming 'user' is the role for clients

            serializer = UserSerializer(clients, many=True)

            return Response({'clients': serializer.data}, status=status.HTTP_200_OK)
        
        
class UserSignUp(APIView):
    def post(request):
        if request.method == 'POST':
            name = request.data.get('name')
            mobile_number = request.data.get('mobile_number')
            otp_input = request.data.get('otp')

            if not name or not mobile_number or not otp_input:
                return Response({'error': 'Name, mobile number, and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(mobile_number=mobile_number)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            
            otp_secret = user.mobile_number
            totp = pyotp.TOTP(otp_secret)
            is_valid_otp = totp.verify(otp_input)

            if not is_valid_otp:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the user account with the role 'user'
            user.name = name  # Update user's name if needed
            user.role = 'user'
            user.save()

            serializer = UserSerializer(user)

            return Response({'message': 'User account created successfully.', 'user_details': serializer.data}, status=status.HTTP_201_CREATED)
        

class AddProduct(APIView):
    def post(request):
        if request.method == 'POST':
            product_name = request.data.get('product_name')
            product_description = request.data.get('product_description')
            category_name = request.data.get('category_name')

            if not product_name or not product_description or not category_name:
                return Response({'error': 'Product name, description, and category are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the category exists, if not, create it
            category, created = Category.objects.get_or_create(name=category_name)

            # Create the product
            product = Product.objects.create(
                name=product_name,
                description=product_description,
                category=category
            )

            product_serializer = ProductSerializer(product)
            category_serializer = CategorySerializer(category)

            response_data = {
                'id': product_serializer.data['id'],
                'name': product_serializer.data['name'],
                'category': category_serializer.data
            }

            return Response({'message': 'Product added successfully.', 'product_details': response_data}, status=status.HTTP_201_CREATED)
        
class AdvisorPurchaseProduct(APIView):
    def post(request):
        if request.method == 'POST':
            advisor = request.user  # Assuming the advisor is the authenticated user
            user_id = request.data.get('user_id')
            product_id = request.data.get('product_id')

            if not user_id or not product_id:
                return Response({'error': 'User ID and product ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(id=user_id, advisor=advisor)
                product = Product.objects.get(id=product_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found or not associated with the advisor.'}, status=status.HTTP_404_NOT_FOUND)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Create the purchase
            purchase = Purchase.objects.create(user=user, product=product)

            purchase_serializer = PurchaseSerializer(purchase)

            return Response({'message': 'Product purchased successfully.', 'purchase_details': purchase_serializer.data}, status=status.HTTP_201_CREATED)