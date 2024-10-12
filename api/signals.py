from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OTP
from .helpers import send_otp_email

@receiver(post_save, sender=OTP)
def send_otp_signal(sender, instance, created, **kwargs):
    print(f"Signal called for OTP with email: {instance.email}")
    if created:
        print( "Signal Called created")
        send_otp_email(instance.email, instance.otp)