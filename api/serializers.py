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
    

############################ Product ##########################

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'sku', 
            'original_price', 'current_price', 'size', 'weight', 
            'burning_time', 'color', 'fragrance', 'in_the_box', 
            'stock', 'tags', 'image_url'
        ]
    
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