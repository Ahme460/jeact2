from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from . models import Customer_user
from django.conf import settings
class SenderMail:
    def __init__(self, subject, content,tem) -> None:
        self.subject = subject
        self.content = content
        self.tem=tem
        
    def send_mail(self, emails):
        context = {
            'title': self.subject,
            'body': self.content,
        }

        # Render the HTML content using the template
        html_content = render_to_string(self.tem, context)
        text_content = strip_tags(html_content)

        # Ensure emails is a list
        if isinstance(emails, str):
            emails = [emails]

        # Ensure there are recipients
        if emails:
            # Send the email to all users
            msg = EmailMultiAlternatives(
                subject=self.subject,                # Subject
                body=text_content,                  # Plain text content
                from_email=settings.DEFAULT_FROM_EMAIL, # From email
                to=emails                           # List of all user emails
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            