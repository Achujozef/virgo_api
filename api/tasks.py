from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email_task (email, otp):
    subject = "Your OTP Code"
    email_body = f'Your OTP code is {otp}. It is valid for the next 5 minutes.'

    try :
        send_mail(
            subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,

        )
        return True
    except Exception as e:
        print(f"Error sending email : {e}")
        return False