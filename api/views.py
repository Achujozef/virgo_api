
from django.http import JsonResponse
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

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

############################## Variant ##################################


# View for creating and listing VariantTypes
class VariantTypeCreateListView(generics.ListCreateAPIView):
    queryset = VariantType.objects.all()
    serializer_class = VariantTypeSerializer

# View for creating and listing VariantOptions
class VariantOptionCreateListView(generics.ListCreateAPIView):
    queryset = VariantOption.objects.all()
    serializer_class = VariantOptionSerializer

############################## Wishlist ##################################

# Add product to wishlist
class AddToWishlistView(generics.CreateAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Automatically set the user to the logged-in user

# Remove product from wishlist
class RemoveFromWishlistView(generics.DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        product_id = self.kwargs['product_id']
        return Wishlist.objects.get(user=user, product_id=product_id)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# List all wishlist items for the user
class WishlistListView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
############################## Cart ##################################

# Add/Update product in cart
class AddToCartView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product')
        variant_id = request.data.get('variant', None)
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
            variant = VariantDetail.objects.get(id=variant_id) if variant_id else None

            add_or_update_cart(user=user, product=product, variant=variant, quantity=quantity)
            return Response({"message": "Cart updated successfully"}, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except VariantDetail.DoesNotExist:
            return Response({"error": "Variant not found"}, status=status.HTTP_404_NOT_FOUND)

# Remove product from cart
class RemoveFromCartView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        product_id = self.kwargs['product_id']
        variant_id = self.kwargs.get('variant_id', None)
        return Cart.objects.get(user=user, product_id=product_id, variant_id=variant_id)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# List all cart items for the user
class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, is_active=True)


# Update quantity of a cart item
class UpdateCartQuantityView(generics.UpdateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        product_id = self.kwargs['product_id']
        variant_id = self.kwargs.get('variant_id', None)
        return Cart.objects.get(user=user, product_id=product_id, variant_id=variant_id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        quantity = int(request.data.get('quantity', instance.quantity))
        if quantity <= 0:
            instance.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)

        instance.quantity = quantity
        instance.save()
        return Response(CartSerializer(instance).data, status=status.HTTP_200_OK)
    
############################## Address ##################################

# Create a new address
class CreateAddressView(generics.CreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# List all addresses for the current user
class ListAddressesView(generics.ListAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

# Update an address (partial updates allowed)
class UpdateAddressView(generics.UpdateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

# Delete an address
class DeleteAddressView(generics.DestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


############################ Order ##########################

class BuyNowView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart_item = request.data.get('cart_item')  # expecting {'product_id': 1, 'quantity': 1}
        order_total = request.data.get('order_total')
        quantity = cart_item.get('quantity', 1)
        product_id = cart_item.get('product_id')

        # Create order
        order_number = f"ORD-{int(timezone.now().timestamp())}"  # Unique order number
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_price=0,  # Price will be calculated later
            status='pending'
        )

        # Add item to order
        order_item = OrderItem.objects.create(
            order=order,
            product_id=product_id,
            quantity=quantity
        )

        order.calculate_total()  # Calculate total price
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

# Buy all products in the cart
class BuyAllFromCartView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user, is_active=True)
        order_total = request.data.get('order_total')

        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        order_number = f"ORD-{int(timezone.now().timestamp())}"  # Unique order number
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_price=0,  # Price will be calculated later
            status='pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity
            )

        order.calculate_total()  # Calculate total price
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

# List all orders
class ListOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(tags=['Orders'])
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# Order detail
class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# Update an order (edit)
class UpdateOrderView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# Delete an order
class DeleteOrderView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


############################ Offer ##########################

# View to list all offers and create a new offer
class OfferListView(generics.ListAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

class OfferCreateView(generics.CreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

# View to retrieve, update, or delete a specific offer by ID
class OfferDetailView(generics.RetrieveAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

class OfferUpdateView(generics.UpdateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

class OfferDeleteView(generics.DestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

############################ Coupen ##########################
# List all coupons
class CouponListView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

# Create a coupon
class CouponCreateView(generics.CreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

# Coupon detail, update, and delete
class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

# Track coupon usage by users
class CouponUsageListView(generics.ListAPIView):
    queryset = CouponUsage.objects.all()
    serializer_class = CouponUsageSerializer





class ApplyCouponView(APIView):
    @swagger_auto_schema(request_body=ApplyCouponSerializer)
    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        if serializer.is_valid():
            coupon_code = serializer.validated_data.get('coupon_code')
            order_total = serializer.validated_data.get('order_total')

            try:
                coupon = Coupon.objects.get(code=coupon_code)
            except Coupon.DoesNotExist:
                return Response({"success": False, "message": "Invalid coupon code."}, status=status.HTTP_400_BAD_REQUEST)

            if not coupon.is_active or not (coupon.start_date <= timezone.now() <= coupon.end_date):
                return Response({"success": False, "message": "Coupon is expired or inactive."}, status=status.HTTP_400_BAD_REQUEST)

            if coupon.minimum_order_amount and Decimal(order_total) < coupon.minimum_order_amount:
                return Response({"success": False, "message": "Order total is less than the minimum required for this coupon."}, status=status.HTTP_400_BAD_REQUEST)

            discounted_price = coupon.apply_discount(Decimal(order_total))

            return Response({"success": True, "discounted_price": discounted_price}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


############################ Testmonials ##########################

# Create Testimonial
class TestimonialCreateView(generics.CreateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

# List Testimonials
class TestimonialListView(generics.ListAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

# Retrieve Testimonial Details
class TestimonialDetailView(generics.RetrieveAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

# Update Testimonial
class TestimonialUpdateView(generics.UpdateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAuthenticated]  # Require authentication to update testimonials


############################ Review ##########################
# Create Review
class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]  # Require authentication to create reviews

# List Reviews
class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Allow any user to see reviews

    def get_queryset(self):
        product_id = self.kwargs['product_id']  # Get the product ID from the URL
        return Review.objects.filter(product_id=product_id)  # Filter reviews by product ID

# Retrieve Review Details
class ReviewDetailView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

# Update Review
class ReviewUpdateView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]  

# List Reviews for a specific Product
class ProductReviewListViewApproved(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Allow any user to see reviews

    def get_queryset(self):
        product_id = self.kwargs['product_id']  # Get the product ID from the URL
        # Filter reviews by product ID and only include approved reviews
        return Review.objects.filter(product_id=product_id, approved=True)
    


############################ Order Message ##########################


# List messages for a specific order
class OrderMessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return Message.objects.filter(order_id=order_id)
    

class OrderMessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        order_id = self.kwargs['order_id']
        user_type = 'user'  # Default to 'user'

        # Set user_type based on the user's role
        if self.request.user.is_staff:
            user_type = 'staff'
        elif self.request.user.is_superuser:
            user_type = 'admin'

        # Save the message
        message = serializer.save(order_id=order_id, sender=self.request.user, user_type=user_type)

        # Determine the recipient based on user type
        subject = ''
        email_body = ''
        recipient_email = ''

        if user_type == 'user':  # If the user sends a message
            subject = 'New Message from User'
            email_body = f"User {self.request.user.username} has sent a message: {message.content}"
            recipient_email = settings.ADMIN_EMAIL  # Assuming admin email is stored in settings

            # Check previous messages sent by the user for this order
            previous_messages = Message.objects.filter(order_id=order_id, sender=self.request.user).order_by('-created_at')

            if not previous_messages.exists():  # If this is the first message
                return Response(
                    {"detail": "Thank you for your message! You are very valuable to us, and we appreciate your order. Our team will contact you shortly."},
                    status=status.HTTP_201_CREATED
                )
            elif (timezone.now() - previous_messages.first().created_at).days >= 1:  # If last message was sent over 24 hours ago
                return Response(
                    {"detail": "Thank you for your message! You are very valuable to us, and we appreciate your order. Our team will contact you shortly."},
                    status=status.HTTP_201_CREATED
                )

        else:  # If staff/admin responds
            subject = 'New Message from Admin/Staff'
            email_body = f"Admin/Staff {self.request.user.username} has responded: {message.content}"
            recipient_email = message.order.user.email  # The user's email from the order

        # Send email notification
        send_notification_email(recipient_email, subject, email_body)

        # If the message is from staff/admin, return a standard response
        return Response(serializer.data, status=status.HTTP_201_CREATED)












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
    permission_classes = [AllowAny]

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
    
class CheckTokenView(View):
    def post(self, request):
        token = request.POST.get('token')
        print("Received Token:", token)  
        return JsonResponse({"message": "Token received", "token": token})
    

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: 'Login successful with JWT tokens',
            400: 'Invalid credentials',
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = serializer.get_tokens(user)

            return Response({
                'refresh': tokens['refresh'],
                'access': tokens['access'],
                'user': {
                    'username': user.username,
                    'email': user.email,
                },
                'message': 'Login successful',
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)