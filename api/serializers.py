from rest_framework import serializers
from .models import *
from .helpers import *
###########################  Category ##################################

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.ListSerializer(child=serializers.DictField(), required=False, write_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'description', 'is_active', 'subcategories']
        
    
    def validate(self, data):
        name = data.get('name', '').strip()
        if len(name) < 3:
            raise serializers.ValidationError({"name": "The category name must be at least 3 characters long."})
        if data.get('parent') is None:
            if Category.objects.filter(name=name, parent__isnull=True).exists():
                raise serializers.ValidationError({"name": "A root category with this name already exists."})
        
        return data
    
    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])
        category = Category.objects.create(**validated_data)
        for subcategory_data in subcategories_data:
            subcategory_data['parent'] = category
            # Recursively create subcategories
            self.create(subcategory_data)
        return category

class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'description', 'is_active']  
        extra_kwargs = {
            'name': {'required': False},
            'parent': {'required': False},
            'description': {'required': False},
            'is_active': {'required': False},
        }
    def validate(self, data):
        name = data.get('name', '').strip()
        if 'name' in data and len(name) < 3:
            raise serializers.ValidationError({"name": "The category name must be at least 3 characters long."})
        if 'parent' in data and data.get('parent') is None:
            if Category.objects.filter(name=name, parent__isnull=True).exists():
                raise serializers.ValidationError({"name": "A root category with this name already exists."})
        
        return data
    

class CategoryTreeSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'description', 'subcategories']

    def get_subcategories(self, obj):
        subcategories = obj.subcategories.filter(is_active=True)
        return CategoryTreeSerializer(subcategories, many=True).data
    


############################ Variant ##########################

class VariantDetailSerializer(serializers.ModelSerializer):
    variant_options = serializers.PrimaryKeyRelatedField(
        queryset=VariantOption.objects.all(),
        many=True
    )
    price_with_offer = serializers.SerializerMethodField()
    

    class Meta:
        model = VariantDetail
        fields = ['variant_options', 'original_price', 'current_price', 'price_with_offer','variant_data','stock']
    
    def get_price_with_offer(self, obj):
        return obj.get_variant_price_with_offer()

class VariantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantType
        fields = ['id', 'name']

class VariantOptionSerializer(serializers.ModelSerializer):
    variant_type = serializers.PrimaryKeyRelatedField(queryset=VariantType.objects.all())

    class Meta:
        model = VariantOption
        fields = ['id', 'variant_type', 'option_value']

############################ Product ##########################

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    variants = VariantDetailSerializer(many=True, required=False)  # Add the nested variants
    price_with_offer = serializers.SerializerMethodField()  # Add this field

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'sku', 
            'original_price', 'current_price', 'price_with_offer','size', 'weight', 
            'burning_time', 'color', 'fragrance', 'in_the_box', 
            'stock', 'tags', 'image_url', 'variants'  # Include variants
        ]
    
    def get_price_with_offer(self, obj):
        """This method computes the price after applying any active offer."""
        return obj.get_price_with_offer()  # This calls the method in the Product model
    
    def validate(self, data):
        if data['original_price'] < data['current_price']:
            raise serializers.ValidationError({
                'current_price': "Current price must be less than or equal to the original price."
            })

        name = data.get('name', '').strip()
        if len(name) < 3:
            raise serializers.ValidationError({
                'name': "The product name must be at least 3 characters long."
            })

        sku = data.get('sku', '').strip()
        if len(sku) < 1:
            raise serializers.ValidationError({
                'sku': "SKU is required."
            })

        return data

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        product = Product.objects.create(**validated_data)

        # Handle the creation of variants
        self._create_variants(product, variants_data)

        return product

    def _create_variants(self, product, variants_data):
        """Helper function to handle variant creation"""
        for variant_data in variants_data:
            variant_options = variant_data.pop('variant_options')
            variant = VariantDetail.objects.create(product=product, **variant_data)
            variant.variant_options.set(variant_options)  # Set the Many-to-Many field
            variant.save()

############################ User ##########################

class OTPSerializer(serializers.Serializer):
    
    email = serializers.EmailField()

    def create_otp(self):
        email = self.validated_data['email']
        otp_instance, created = OTP.objects.get_or_create(email=email)
        otp_instance.generate_otp()
        send_otp_email(email, otp_instance.otp)
        return otp_instance
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        ExtendedUserModel.objects.create(user=user)
        return user
    
class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Invalid credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        data['user'] = user
        return data

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

############################ Wishlist ##########################

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'added_at']
        read_only_fields = ['id', 'added_at']

    # Ensure that a user cannot add the same product multiple times
    def validate(self, data):
        user = data['user']
        product = data['product']
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("This product is already in the wishlist.")
        return data

############################ Cart ##########################

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'variant', 'quantity', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']

    def validate(self, data):
        # Ensure product and variant combination is valid
        product = data.get('product')
        variant = data.get('variant')

        if variant and variant.product != product:
            raise serializers.ValidationError("The variant does not belong to the selected product.")
        
        return data

############################ Address ##########################

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'address_line_1', 'address_line_2', 'city', 'state', 'country', 'postal_code']
        read_only_fields = ['id', 'user']

############################ Order ##########################

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_number', 'status', 'total_price', 'shipping_address', 'billing_address', 'created_at', 'updated_at', 'items']
        read_only_fields = ['id', 'user', 'order_number', 'total_price', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order
    

############################ Offer ##########################

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

    def validate(self, attrs):
        """Validate offer dates and ensure only one active offer per product/category."""
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        
        if attrs['offer_type'] == 'product':
            if Offer.objects.filter(product=attrs['product'], is_active=True).exists():
                raise serializers.ValidationError("There is already an active offer for this product.")
        elif attrs['offer_type'] == 'category':
            if Offer.objects.filter(category=attrs['category'], is_active=True).exists():
                raise serializers.ValidationError("There is already an active offer for this category.")
        
        return attrs