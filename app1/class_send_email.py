from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from . models import Customer_user
from django.conf import settings
class Sender_mail:
    def __init__(self,subject,content) -> None:
        self.subject=subject
        self.content=content
        
    def send_mail(self,email):
        context = {
                'title': self.subject,
                'body': self.content,
            }

            # Render the HTML content using the template
        html_content = render_to_string('email_template.html', context)
        text_content = strip_tags(html_content)

        # Get all user email addresses
        recipients = email

        # Ensure there are recipients
        if recipients:
            # Send the email to all users
            msg = EmailMultiAlternatives(
                self.subject,  # Subject
                self.content,
                #text_content,  # Plain text content
                settings.eDEFAULT_FROM_EMAIL,  # From email
                recipients  # List of all user emails
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            
            