from django.core.mail import send_mail
from django.conf import settings
from .models import Cart ,Coupon , CouponUsage
from .tasks import send_otp_email_task , send_notification_email


def send_otp_email(email, otp):
    send_otp_email_task.delay(email, otp)

def add_or_update_cart(user, product, variant, quantity):
    try:
        cart_item = Cart.objects.get(user=user, product=product, variant=variant)
        cart_item.quantity += quantity

        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()

    except Cart.DoesNotExist:
        if quantity > 0:
            Cart.objects.create(user=user, product=product, variant=variant, quantity=quantity)


def apply_coupon_to_order(coupon_code, order, user):
    """Apply the coupon to the given order."""
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        return {"success": False, "message": "Coupon does not exist."}

    if not coupon.is_valid(user, order.total_price):
        return {"success": False, "message": "Coupon is not valid."}

    discounted_price = coupon.apply_discount(order.total_price)

    CouponUsage.objects.create(user=user, coupon=coupon)
    
    order.total_price = discounted_price
    order.save()
    
    return {"success": True, "discounted_price": discounted_price}


def send_notification_email(email, subject, message):
    send_notification_email.delay(email, subject, message)