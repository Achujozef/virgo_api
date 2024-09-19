
import random
from django.utils import timezone
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

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