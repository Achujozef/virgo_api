from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OTP
from .helpers import send_otp_email

@receiver(post_save, sender=OTP)
def send_otp_signal(sender, instance, created, **kwargs):
    if created:
        send_otp_email(instance.email, instance.otp)