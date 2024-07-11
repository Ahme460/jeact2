
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from celery import shared_task
from django.conf import settings
from app1.models import Customer_user
User = get_user_model()
def send_welcome_email(user_email):
    send_mail(
        'Welcome!',
        'Thank you for signing up!',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )
def send_reset_password_email(user):
    try:
        # print(user)
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f'http://127.0.0.1:8000/reset-password/{uid}/{token}/'

        from django.core.mail import EmailMessage
        email_sender = EmailMessage(
            subject='Password Reset',
            body=f'Click the link below to reset your password:\n{reset_link}',
            to=[user.email],
        )
        email_sender.send()
        return True
    except User.DoesNotExist:
        return False
 
    
@shared_task
def send_email_task(subject, message):
    users = Customer_user.objects.all()
    for user in users:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

