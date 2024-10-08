from django.core.mail import send_mail
from django.conf import settings
from .models import Cart ,Coupon , CouponUsage

def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    email_body = f'Your OTP code is {otp}. It is valid for the next 5 minutes.'
    
    try:
        send_mail(
            subject,
            email_body,
            settings.EMAIL_HOST_USER,  
            [email],  
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

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

    # Apply the discount to the total price
    discounted_price = coupon.apply_discount(order.total_price)

    # Track coupon usage
    CouponUsage.objects.create(user=user, coupon=coupon)
    
    # Update order total
    order.total_price = discounted_price
    order.save()
    
    return {"success": True, "discounted_price": discounted_price}


def send_notification_email(email, subject, message):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender's email
            [email],  # Recipient's email
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False