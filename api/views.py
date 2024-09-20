
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema


from .otp_utils import verify_otp, get_or_create_user, issue_jwt_token
from .serializers import *
from .paginations import ProductPagination
# Create your views here.

############################## Category View ##############################

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategoryTreeSerializer
    def get_queryset(self):
        return Category.objects.filter(is_active = True, parent__isnull=True)

class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryUpdateSerializer

    def patch(self, request, *args, **kwargs):
        # Allow partial updates
        return self.update(request, *args, **kwargs)
    
############################## Product View ##############################


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()  
    serializer_class = ProductSerializer
    pagination_class = ProductPagination 

class ProductListByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination  
    def get_queryset(self):
        category = self.kwargs['category_id']
        return Product.objects.filter(category__id=category)
    
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


############################## User View ##################################
# from drf_yasg.utils import swagger_auto_schema
# class OTPGenerationView(APIView):
#     @swagger_auto_schema(
#         request_body=OTPSerializer,
#         responses={200: 'OTP sent to email.'}
#     )
#     def post(self, request):
#         serializer = OTPSerializer(data=request.data)
#         if serializer.is_valid():
#             otp_instance = serializer.create_otp()
#             return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPGenerationView(generics.CreateAPIView):
    serializer_class = OTPSerializer
    queryset = OTP.objects.all()  # Required by generics

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            otp_instance = serializer.create_otp()  # Use the method from the serializer to generate OTP
            return Response({"message": "OTP sent to email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OTPVerificationView(generics.CreateAPIView):
    serializer_class = OTPVerificationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=OTPVerificationSerializer,
        responses={
            200: 'Login/Registration successful with JWT tokens',
            400: 'Invalid OTP',
            404: 'OTP not found for this email'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            if verify_otp(email, otp):
                user, created = get_or_create_user(email)
                tokens = issue_jwt_token(user)

                return Response({
                    'refresh': tokens['refresh'],
                    'access': tokens['access'],
                    'user': {
                        'email': user.email,
                        'username': user.username,
                    },
                    'message': 'Login successful' if not created else 'Registration successful'
                }, status=status.HTTP_200_OK)

            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)