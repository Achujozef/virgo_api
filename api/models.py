from django.db import models
from django.contrib import admin


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
