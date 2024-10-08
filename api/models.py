
import random
from django.utils import timezone
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings
from django.contrib.postgres.fields import JSONField 
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='subcategories', 
        blank=True, 
        null=True
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.name}"

    def get_subcategories(self):
        return self.subcategories.filter(is_active=True)

    def get_ancestors(self):
        """
        Returns a list of all parent categories up to the root.
        """
        categories = []
        current_category = self
        while current_category.parent is not None:
            categories.append(current_category.parent)
            current_category = current_category.parent
        return categories

    def get_descendants(self):
        """
        Returns a list of all subcategories down to the leaf nodes.
        """
        descendants = []
        for subcategory in self.get_subcategories():
            descendants.append(subcategory)
            descendants.extend(subcategory.get_descendants())
        return descendants


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=100)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=50)  # e.g., LxBxH or volume
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # in grams
    burning_time = models.CharField(max_length=50)  # e.g., 1-2 hours
    color = models.CharField(max_length=50)
    fragrance = models.CharField(max_length=100)
    in_the_box = models.TextField()  # e.g., '5 pcs Nilofer floating candles'
    stock = models.PositiveIntegerField()
    tags = models.CharField(max_length=255, blank=True)  # For additional filtering or metadata
    image_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name

    def get_price_with_offer(self):
        """
        Returns the product price after applying any active offer.
        If a variant exists, the variant price will be used.
        """
        now = timezone.now()

        # Check if there is an active product-specific offer
        product_offer = Offer.objects.filter(
            product=self, 
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()

        if product_offer:
            # Apply product-level offer
            return product_offer.apply_discount(self.current_price)

        # Check if there's a category-level offer if no product offer exists
        category_offer = Offer.objects.filter(
            category=self.category,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()

        if category_offer:
            # Apply category-level offer
            return category_offer.apply_discount(self.current_price)

        # No offers available, return the original product price
        return self.current_price




class ExtendedUserModel(models.Model):
    def __str__(self):
        return self.user.username
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    USER_TYPE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('user', 'User'),
    ]

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='extendedusermodel',blank=True,null=True)
    phone = models.CharField(max_length=20,blank=True,null=True)
    profile_photo = models.ImageField(upload_to='profile_photos', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')  
    created_at = models.DateTimeField(default=timezone.now)


class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        self.otp = f"{random.randint(1000, 9999)}"
        self.created_at = timezone.now()
        self.save()

    def is_valid(self):
        time_elapsed = timezone.now() - self.created_at
        return time_elapsed.seconds < 300  
    
class VariantType(models.Model):
    name = models.CharField(max_length=100)  # e.g., 'Color', 'Size'

    def __str__(self):
        return self.name

class VariantOption(models.Model):
    variant_type = models.ForeignKey(VariantType, on_delete=models.CASCADE, related_name='options')
    option_value = models.CharField(max_length=100)  # e.g., 'Red', 'Large'

    def __str__(self):
        return f"{self.variant_type.name} - {self.option_value}"

class VariantDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_options = models.ManyToManyField(VariantOption)  # Many-to-Many for multiple options (e.g., size + color)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)    
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    variant_data = models.JSONField(null=True, blank=True)  # Storing variants dynamically as key-value pairs
    def __str__(self):
        variants = ', '.join([f"{key}: {value}" for key, value in self.variant_data.items()])
        return f"{self.product.name} - {variants}"
    
    def get_variant_price_with_offer(self):
        """
        Returns the variant price after applying any active offer.
        Offers can apply to either the product or the category.
        """
        now = timezone.now()

        # Check if there's a product-specific offer
        product_offer = Offer.objects.filter(
            product=self.product,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()

        if product_offer:
            # Apply product-level offer
            return product_offer.apply_discount(self.current_price)

        # Check for category-level offer if no product offer exists
        category_offer = Offer.objects.filter(
            category=self.product.category,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()

        if category_offer:
            # Apply category-level offer
            return category_offer.apply_discount(self.current_price)

        # No offers available, return the original variant price
        return self.current_price

    def __str__(self):
        variants = ', '.join([f"{opt.variant_type.name}: {opt.option_value}" for opt in self.variant_options.all()])
        return f"{self.product.name} - {variants}"
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)  # When the product was added to the wishlist

    class Meta:
        unique_together = ('user', 'product')  # To prevent duplicates for the same user

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.product.name}"
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_products')
    variant = models.ForeignKey(VariantDetail, on_delete=models.SET_NULL, blank=True, null=True, related_name='cart_variant')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # To track active cart items

    def __str__(self):
        return f"{self.user.user.username}'s cart - {self.product.name} ({self.quantity})"



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.country}"
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipping_orders')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_orders')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

    def calculate_total(self):
        total = 0
        for item in self.items.all():
            total += item.get_total_price()
        self.total_price = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(VariantDetail, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.product.name} (Order: {self.order.order_number})"

    def get_total_price(self):
        if self.variant:
            return self.variant.current_price * self.quantity
        return self.product.current_price * self.quantity
    

class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('product', 'Product'),
        ('category', 'Category'),
    ]

    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=255)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)  # Discount amount or percentage
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Relations to Product or Category
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='offers', blank=True, null=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.get_offer_type_display()}"

    def is_valid(self):
        """Checks if the offer is within the valid time frame."""
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.is_active

    def apply_discount(self, price):
        """Applies the offer to a given price based on the discount type."""
        if self.discount_type == 'percentage':
            discount_amount = price * (self.discount_value / Decimal('100'))
            return price - discount_amount
        elif self.discount_type == 'fixed':
            return max(price - self.discount_value, Decimal('0'))  # Ensure price doesn't go below 0
        return price


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit_per_user = models.PositiveIntegerField(default=1)  # How many times a user can use this coupon
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Relations to Product or Category (optional)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='coupons', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='coupons', blank=True, null=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Coupon {self.code} ({self.discount_type} - {self.discount_value})"

    def is_valid(self, user, order_total):
        """Check if the coupon is valid for the user and the order."""
        now = timezone.now()
        if not (self.start_date <= now <= self.end_date) or not self.is_active:
            return False
        
        if self.minimum_order_amount and order_total < self.minimum_order_amount:
            return False

        usage_count = CouponUsage.objects.filter(user=user, coupon=self).count()
        if usage_count >= self.usage_limit_per_user:
            return False

        return True

    def apply_discount(self, price):
        """Applies the coupon discount to a given price based on the discount type."""
        if self.discount_type == 'percentage':
            return price * (1 - (self.discount_value / 100))
        elif self.discount_type == 'fixed':
            return max(price - self.discount_value, Decimal('0.00'))  # Ensure the price doesn't go below zero
        return price


class CouponUsage(models.Model):
    """Tracks how many times a user has used a coupon."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} used {self.coupon.code} on {self.used_at}"
    

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Assuming you have a Product model
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who made the review
    review_text = models.TextField()  # The content of the review
    rating = models.PositiveIntegerField(null=True, blank=True)  # Rating, e.g., 1 to 5 stars
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the date when created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set the date when updated
    approved = models.BooleanField(default=False)  # Indicates if the review is approved

    def __str__(self):
        return f"Review for {self.product} by {self.user.username}: {self.review_text[:50]}..."  # Show the first 50 characters

    class Meta:
        ordering = ['-created_at']  # Order reviews by latest first



class Testimonial(models.Model):
    name = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    testimonial_text = models.TextField()  # The content of the testimonial
    rating = models.PositiveIntegerField(null=True, blank=True)  # Optional rating, e.g., 1 to 5 stars
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the date when created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set the date when updated
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Testimonial by {self.name}: {self.testimonial_text[:50]}..."  # Show the first 50 characters

    class Meta:
        ordering = ['-created_at']  # Order testimonials by latest first


class Message(models.Model):
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')

    def __str__(self):
        return f"Message from {self.sender.username} for Order {self.order.order_number}: {self.content[:50]}"