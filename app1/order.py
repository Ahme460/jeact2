from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_order_mail(user,list):
    subject = 'مرحبا بك في موقعنا!'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email=user.email
    
    
    
    # تحميل القالب HTML وتعبئته بالبيانات
    html_content = render_to_string(
        
                    'fatora.html',
                    {'list': list}
                                    
                                    )
    text_content = strip_tags(html_content)  # نص بديل بدون HTML
    
    # إنشاء البريد الإلكتروني
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")  # إرفاق القالب HTML
    
    # إرسال البريد
    email.send()
