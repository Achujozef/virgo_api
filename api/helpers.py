from django.core.mail import send_mail
from django.conf import settings
from .models import Cart

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
