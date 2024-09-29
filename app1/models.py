from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import requests
#from countryinfo import CountryInfo
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.utils import timezone
class categories(models.Model):
    name=models.CharField(max_length=100)
    descrtion=models.TextField()
    
    def __str__(self) -> str:
        return self.name
    
    
class DiscountCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # نسبة الخصم
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # مبلغ الخصم
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_until
   
   
# نموذج الدول
class Country(models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.name
class Province(models.Model):
    name = models.CharField(max_length=200)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='provinces')
    delivery_price = models.FloatField(validators=[MinValueValidator(0.0)])
    def __str__(self):
        return f'{self.name}, {self.country.name}'
    

# تعديل نموذج المستخدم
class Customer_user(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='users')
    currence=models.CharField(max_length=50)
    def save(self, *args, **kwargs):
       # self.password=make_password(self.password)
        super().save(*args, **kwargs)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

   # def set_currency(self):
      #  country = CountryInfo(self.country.name)
       # return country.currencies()[0] if country.currencies() else "Unknown"



from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.dispatch import receiver 
from django.conf import settings
from .tasks import send_email_task
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from email.mime.image import MIMEImage

from django.contrib.sites.models import Site
from django.urls import reverse



class sender_email(models.Model):
    subject=models.CharField(max_length=100)
    pic_email=models.ImageField(blank=True,upload_to='email_images/')
    content=models.TextField()
    def __str__(self) -> str:
        
       return self.subject

@receiver(post_save, sender=sender_email)
def send_message(sender, instance, created, **kwargs):
    if created:
        # Get the current site URL
        current_site = Site.objects.get_current()
        domain = current_site.domain
        
        # Construct the absolute URL for the image
        image_url = f"https://api.bantayga.wtf/media/{instance.pic_email.name}"

        # Use the selected email template
        context = {
            'title': instance.subject,
            'body': instance.content,
            'image_url': image_url
        }

        # Render the HTML content using the template
        html_content = render_to_string('email_template.html', context)
        text_content = strip_tags(html_content)

        # Get all user email addresses
        recipients = list(Customer_user.objects.values_list('email', flat=True))

        # Ensure there are recipients
        if recipients:
            # Send the email to all users
            msg = EmailMultiAlternatives(
                instance.subject,  # Subject
                text_content,  # Plain text content
                settings.DEFAULT_FROM_EMAIL,  # From email
                recipients  # List of all user emails
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
     
        #else:
            # Fallback if no template is selected
           # send_email_task(instance.subject, instance.content)
# نموذج المنتجات
class Products(models.Model):
    SALE_CHOICES = [
        ('sale', 'Sale'),
        ('sale_out', 'Sale Out'),
        ('sold_out','sold_out'),
        ('none','none'),
    ]
    SIZE_SELECT = [
        ('small', 's'),
        ('medium', 'm'),
        ('large', 'l'),
        ('Xs','xs'),
        ('Xl','xl'),
        ('XXl','xxl')
        
    ]
    
    name = models.CharField(max_length=50)
    price = models.FloatField()
    categray = models.ForeignKey(categories, on_delete=models.CASCADE, related_name='products')
    about_product = models.TextField()
    photo = models.FileField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sale_status = models.CharField(max_length=10, choices=SALE_CHOICES, default='sale')
    details = models.TextField()
    Discount = models.FloatField(blank=True,null=True,default=0) # حقل الخصم كنسبة مئوية
    #size = models.CharField(max_length=50, null=True, choices=SIZE_SELECT)
    is_featured = models.BooleanField(default=False, verbose_name="Featured on Homepage")   
    count=models.IntegerField(default=1)
    
    
    
    def get_discounted_price(self):
        return self.price - (self.price * (self.discount / 100))

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name

    def convert_price(self, user_currency):
        if user_currency != 'EGP':
            try:
                url = 'https://v6.exchangerate-api.com/v6/a8337073c983fa5ad505f498/latest/EGP'
                response = requests.get(url)
                data = response.json()
                conversion_rate = data['conversion_rates'].get(user_currency)
                if conversion_rate:
                    return self.price * conversion_rate
                else:
                    return self.price
            except Exception as e:
                return self.price
        return self.price



class Wishlist(models.Model):
    user = models.ForeignKey(Customer_user, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # يمنع إضافة نفس المنتج أكثر من مرة للمستخدم نفسه

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"




class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.product.name}"



# نموذج الأحجام
class SizesModel(models.Model):
    SIZE_SELECT = [
        ('small', 's'),
        ('medium', 'm'),
        ('large', 'l'),
        ('Xs','xs'),
        ('Xl','xl'),
        ('XXl','xxl')
        
    ]
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="sizes")
    size = models.CharField(max_length=50, null=True, choices=SIZE_SELECT)
    descrtions_size_fit=models.TextField(null=True)
    count=models.PositiveIntegerField(default=0)
    
    
    def __str__(self) -> str:
        return f"{self.size} {self.product}"
    

class ColorsModel(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="colors")
    color = models.CharField(max_length=50, null=True)
    
    def __str__(self) -> str:
        return f"{self.color} {self.product}"
    


class Orders(models.Model):
    order = models.TextField()
    customer = models.ForeignKey(Customer_user, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=True)
    phone_user = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    location = models.TextField()

    def __str__(self):
        return self.customer.username if self.customer else 'No Customer'

class CartModel(models.Model):
    customer = models.OneToOneField(Customer_user, on_delete=models.CASCADE, related_name="cart")
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self) -> str:
        return self.customer.username
     #total = sum([(item.product.price - item.product.Discount) * item.quantity for item in self.items.all()])
    @property
    def total_price(self):
        total = 0
        for item in self.items.all():
            # التحقق من وجود سعر المنتج والخصم باستخدام 0 كقيمة افتراضية إذا كان أي منهما None
            price = item.product.price or 0
            discount = item.product.Discount or 0
            quantity = item.quantity or 1

            # إذا لم يكن هناك خصم، يتم استخدام السعر الأصلي
            if discount <= 0:
                total += price * quantity
            else:
                # إذا كان هناك خصم، يتم استخدامه بدلاً من السعر الأصلي
                total += discount * quantity

        # إذا كان هناك كود خصم، يتم تطبيقه على المجموع الكلي
        if self.discount_code and self.discount_code.is_valid():
            if self.discount_code.discount_percentage:
                # تطبيق نسبة الخصم
                total -= total * (self.discount_code.discount_percentage / 100)
            elif self.discount_code.discount_amount:
                # تطبيق قيمة الخصم الثابتة
                total -= self.discount_code.discount_amount

        return total


class CartItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE,related_name="product_cart")
    quantity = models.PositiveIntegerField(default=0)
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name="items", null=True)
    size = models.CharField(max_length=50,default='none')
    color = models.CharField(max_length=50,default='none')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} ({self.size}, {self.color})'


class ContactUs(models.Model):
    name = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=100)
    message = models.TextField()


#class Currence(models.Model):
    #user = models.ForeignKey(Customer_user, on_delete=models.CASCADE)
    #currency = models.CharField(max_length=50)


class Address(models.Model):
    user = models.ForeignKey(Customer_user, on_delete=models.CASCADE)
    country=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    detal=models.TextField()
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, related_name='addresses')

    
    

class Social_media(models.Model):
    name=models.CharField(max_length=50,null=True)
    logo=models.ImageField(upload_to='social_media',null=True)
    link=models.CharField(max_length=500,null=True)
    descrtion=models.TextField(null=True)


    
class Text_pic_wep(models.Model):
    based_pic = models.ImageField(upload_to='pic_wep', null=True, blank=True)
    based_pic2 = models.ImageField(upload_to='pic_wep', null=True, blank=True)
    based_pic3 = models.ImageField(upload_to='pic_wep', null=True, blank=True)
    logo = models.ImageField(upload_to='pic_wep', null=True, blank=True)
    about_us_pic = models.ImageField(upload_to='pic_wep', null=True, blank=True)
    about_us = models.TextField(null=True, blank=True)
    contect_us = models.TextField(null=True, blank=True)
    contect_us_pic = models.ImageField(upload_to='pic_wep', null=True, blank=True)
    trademark = models.CharField(max_length=400, null=True, blank=True)
