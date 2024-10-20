from django.contrib import admin
from .models import *
from django.urls import path
from django.utils.html import format_html
from django.contrib.auth.hashers import make_password
from .views import generate_order_pdf
class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name']

class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ['name']

class CustomerUserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'first_name', 'last_name']
    
    # هنا يتم تشفير كلمة المرور عند الحفظ
    def save_model(self, request, obj, form, change):
        # التحقق إذا كانت كلمة المرور جديدة أو غير مشفرة
        if 'password' in form.cleaned_data and not obj.password.startswith('pbkdf2_sha256$'):
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
class ProductsAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']

class SizesModelAdmin(admin.ModelAdmin):
    search_fields = ['size']

class ColorsModelAdmin(admin.ModelAdmin):
    search_fields = ['color']

class OrdersAdmin(admin.ModelAdmin):
    search_fields = ['order_number', 'customer__email']
    list_display = ['order_number', 'customer_email', 'pdf_link'] 
    
    def customer_email(self, obj):
        return obj.customer.email
    
    # إضافة رابط لتوليد PDF في العمود الجديد
    def pdf_link(self, obj):
        url = reverse('admin-generate-pdf', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Generate PDF</a>', url)
    
    pdf_link.short_description = 'Generate PDF'

    # إضافة رابط عرض مخصص لتوليد PDF في الـ URLs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-pdf/<int:order_id>/', self.admin_site.admin_view(generate_order_pdf), name='admin-generate-pdf'),
        ]
        return custom_urls + urls
    
    

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

class CategrayAdmin(admin.ModelAdmin):
    search_fields = ["name"]

class SocialMediAdmin(admin.ModelAdmin):
    search_fields = ["name"]

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
admin.site.register(categories, CategrayAdmin)
admin.site.register(Social_media, SocialMediAdmin)
admin.site.register(ProductImage)
admin.site.register(Text_pic_wep)
admin.site.register(DiscountCode)
admin.site.register(Newsletter)
