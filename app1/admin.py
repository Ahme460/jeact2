from django.contrib import admin
from .models import *

class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name']  # الحقول التي تريد البحث فيها

class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ['name']

class CustomerUserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'first_name', 'last_name']  # البحث بواسطة البريد الإلكتروني، الاسم الأول، والاسم الأخير

class ProductsAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']

class SizesModelAdmin(admin.ModelAdmin):
    search_fields = ['size']

class ColorsModelAdmin(admin.ModelAdmin):
    search_fields = ['color']

class OrdersAdmin(admin.ModelAdmin):
    search_fields = ['order_number', 'customer__email']  # البحث بواسطة رقم الطلب وبريد العميل

class CartModelAdmin(admin.ModelAdmin):
    search_fields = ['user__email']

class CartItemAdmin(admin.ModelAdmin):
    search_fields = ['product__name']

class ContactUsAdmin(admin.ModelAdmin):
    search_fields = ['email', 'message']

class AddressAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'address']

class SenderEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']

class Categray_admin(admin.ModelAdmin):
    search_fields=["name"]
    

admin.site.register(Country, CountryAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Customer_user, CustomerUserAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(SizesModel, SizesModelAdmin)
admin.site.register(ColorsModel, ColorsModelAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(CartModel, CartModelAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(sender_email, SenderEmailAdmin)
admin.site.register(categories, Categray_admin)

admin.site.register(ProductImage)

#models = [Customer_user, Products, SizesModel, ColorsModel, CartItem, Orders, CartModel,Currence]
# Register your models here.
# admin.site.register(Customer_user)