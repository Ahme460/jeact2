from django.contrib import admin
from .models import *

#models = [Customer_user, Products, SizesModel, ColorsModel, CartItem, Orders, CartModel,Currence]

admin.site.register(Country)
admin.site.register(Province)
admin.site.register(Customer_user)
admin.site.register(Products)
admin.site.register(SizesModel)
admin.site.register(ColorsModel)
admin.site.register(Orders)
admin.site.register(CartModel)
admin.site.register(CartItem)
admin.site.register(ContactUs)
admin.site.register(Address)
admin.site.register(sender_email)
# Register your models here.
# admin.site.register(Customer_user)