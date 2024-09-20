from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP

def verify_otp(email, otp):
    try:
        otp_instance = OTP.objects.get(email=email)
        if otp_instance.is_valid() and otp_instance.otp == otp:
            return True
        return False
    except OTP.DoesNotExist:
        return False

def get_or_create_user(email):
    user, created = User.objects.get_or_create(email=email, defaults={"username": email})
    if created:
        user.set_unusable_password()  
        user.save()
    return user, created

def issue_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }
