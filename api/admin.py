from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CouponUsage)
admin.site.register(Coupon)
admin.site.register(Offer)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(Wishlist)
admin.site.register(VariantDetail)
admin.site.register(VariantOption)
admin.site.register(VariantType)
admin.site.register(OTP)
admin.site.register(ExtendedUserModel)

