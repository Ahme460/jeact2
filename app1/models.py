from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import requests
#from countryinfo import CountryInfo
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
   

    
class categories(models.Model):
    name=models.CharField(max_length=100)
    descrtion=models.TextField()
    
    def __str__(self) -> str:
        return self.name
    

   
   
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
class sender_email(models.Model):
    subject=models.CharField(max_length=100)
    content=models.TextField()
    def __str__(self) -> str:
        self.subject

@receiver(post_save, sender=sender_email)
def send_message(sender, instance, created, **kwargs):
    if created:
        send_email_task(instance.subject, instance.content)
        









# نموذج المنتجات
class Products(models.Model):
    SALE_CHOICES = [
        ('sale', 'Sale'),
        ('sale_out', 'Sale Out'),
    ]
    SIZE_SELECT = [
        ('small', 's'),
        ('medium', 'm'),
        ('large', 'l'),
    ]
    name = models.CharField(max_length=50)
    price = models.FloatField()
    categray=models.ForeignKey(categories,on_delete=models.CASCADE, related_name='products')
    about_product = models.TextField()
    photo = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sale_status = models.CharField(max_length=10, choices=SALE_CHOICES, default='sale')
    details = models.TextField()

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

# نموذج الأحجام
class SizesModel(models.Model):
    SIZE_SELECT = [
        ('small', 's'),
        ('medium', 'm'),
        ('large', 'l'),
    ]
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="sizes")
    size = models.CharField(max_length=50, null=True, choices=SIZE_SELECT)
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
    def __str__(self) -> str:
        return self.customer.username
    
    @property
    def total_price(self):
        return sum([item.product.price * item.quantity for item in self.items.all()])


class CartItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name="items", null=True)
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
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

    
    
    
