# from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from .serializers import RegisterSerializer, UserSerializer
# from rest_framework_simplejwt.tokens import RefreshToken


# class RegisterAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             user = User.objects.get(username = serializer.data['username'])
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "message": "User created successfully",
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token)
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user:
#             return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
#         return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

# class UserDetailAPIView(APIView):

#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         users = User.objects.all() 
#         serializer = UserSerializer(users, many=True) 
#         return Response(serializer.data, status=status.HTTP_200_OK)


from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import RegisterSerializer, UserSerializer , UserUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .authentication import CookieJWTAuthentication
from django.contrib.auth.hashers import check_password




import hashlib
import datetime
from django.conf import settings

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Save user and create Profile in the serializer
            refresh = RefreshToken.for_user(user)
            response = Response({
                "message": "User created successfully",
                "action" : "success",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile": {
                        "city": user.profile.city,
                        "contact": user.profile.contact,
                        "role": user.profile.role,
                    },
                }
            }, status=status.HTTP_201_CREATED)
            # Set cookies for refresh and access tokens
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=True,  # Set to True in production
                samesite='None',
                expires=datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,  # Set to True in production
                samesite='None',
                expires=datetime.datetime.utcnow() + datetime.timedelta(days=7)
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            response = Response({
                "message": "Login successful",
                "action" : "success",

                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile": {
                        "city": user.profile.city,
                        "contact": user.profile.contact,
                        "role": user.profile.role,
                    },
                }
            }, status=status.HTTP_200_OK)
            # Set cookies for refresh and access tokens
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=True,  # Set to True in production
                samesite='None',
                expires=datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,  # Set to True in production
                samesite='None',
                expires=datetime.datetime.utcnow() + datetime.timedelta(days=7)
            )
            return response
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserDetailAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        user = request.user  # Get the currently authenticated user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token not found in cookies"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            response = Response({
                "message": "Access token refreshed successfully",
            }, status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=str(access_token),
                httponly=True,
                secure=True,  # Set to True in production
                samesite='None',
                expires=datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            )
            return response
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({
            "message": "Logout successful",
             "action" : "success",

        }, status=status.HTTP_200_OK)
        
        # Delete cookies for access and refresh tokens
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

      
        return response

class UserAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the currently authenticated user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)  

    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """
        Handle password update.
        """
        user = request.user
        data = request.data

        # Validate required fields
        previous_password = data.get("previous_password")
        new_password = data.get("new_password")
        reenter_password = data.get("reenter_password")

        if not previous_password or not new_password or not reenter_password:
            return Response(
                {"message": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if previous password matches the current password
        if not check_password(previous_password, user.password):
            return Response(
                {"message": "Previous password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if new password matches re-entered password
        if new_password != reenter_password:
            return Response(
                {"message": "New password and re-entered password do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the user's password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password updated successfully." , "action" : "success",
},
            status=status.HTTP_200_OK,
        )


class CreatePaymentAPIView(APIView):
    def post(self, request):

        plan = request.data.get('plan')  # Use request.data for JSON POST data
        amount = {
            'basic': 29,
            'standard': 99,
            'premium': 499
        }.get(plan, 0)

        if not amount:
            return Response({'error': 'Invalid plan selected'}, status=status.HTTP_400_BAD_REQUEST)

        # JazzCash credentials
        merchant_id = settings.JAZZCASH_MERCHANT_ID
        password = settings.JAZZCASH_PASSWORD
        integrity_salt = settings.JAZZCASH_INTEGRITY_SALT
        date_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        post_data = {
            'pp_Version': '1.1',
            'pp_TxnType': 'MWALLET',
            'pp_Language': 'EN',
            'pp_MerchantID': merchant_id,
            'pp_Password': password,
            'pp_Amount': str(int(amount * 100)),  # Amount in paisa
            'pp_TxnRefNo': f'TXN-{date_time}',
            'pp_Description': f'Subscription for {plan} plan',
            'pp_TxnDateTime': date_time,
            'pp_BillReference': 'billRef',
            'pp_TransactionID': '',
            'pp_ReturnURL': 'http://127.0.0.1:8000/',
        }

        # Generate secure hash
        sorted_keys = sorted(post_data.keys())
        hash_string = '&'.join(f'{key}={post_data[key]}' for key in sorted_keys)
        hash_string = integrity_salt + '&' + hash_string
        secure_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        post_data['pp_SecureHash'] = secure_hash

        # JazzCash payment URL
        payment_url = 'https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform.aspx'

        return Response({'paymentUrl': payment_url, 'postData': post_data , "action" : "success",}, status=status.HTTP_200_OK)
    def get(self, request):

        return Response({'message' : "working"}, status=status.HTTP_200_OK)

