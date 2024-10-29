from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_order_mail(user,list,name):
    subject = 'مرحبا بك في موقعنا!'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email=user.email
    html_content = render_to_string(
        
                    'fatora.html',
                    {'list': list,"name":name}
                                    
                                    )
    text_content = strip_tags(html_content)  
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")  
    

    email.send()
