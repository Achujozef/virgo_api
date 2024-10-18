from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
    
@shared_task
def send_notification_email(email, subject, message):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER, 
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

channel_layer = get_channel_layer()

async_to_sync(channel_layer.group_send)(
    'staff_notifications',
    {
        'type': 'send_notification',
        'message': 'New message for staff'
    }
)

async_to_sync(channel_layer.group_send)(
    'admin_notifications',
    {
        'type': 'send_notification',
        'message': 'New message for admin'
    }
)