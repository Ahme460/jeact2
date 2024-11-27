from django.contrib import admin
from .models import *
from django.urls import path
from django.utils.html import format_html
from django.contrib.auth.hashers import make_password
from .views import generate_order_pdf
from unfold.admin import ModelAdmin
class CountryAdmin(ModelAdmin):
    search_fields = ['name']

class ProvinceAdmin(ModelAdmin):
    search_fields = ['name']

class CustomerUserAdmin(ModelAdmin):
    search_fields = ['email', 'first_name', 'last_name']
    
    # هنا يتم تشفير كلمة المرور عند الحفظ
    def save_model(self, request, obj, form, change):
        # التحقق إذا كانت كلمة المرور جديدة أو غير مشفرة
        if 'password' in form.cleaned_data and not obj.password.startswith('pbkdf2_sha256$'):
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
class ProductsAdmin(ModelAdmin):
    search_fields = ['name', 'description']
    list_display = ['name', 'details']  # عرض الحقل في القائمة
    fields = ['name', 'details']  # الحقول التي ستظهر عند التعديل

class SizesModelAdmin(ModelAdmin):
    search_fields = ['size']

class ColorsModelAdmin(ModelAdmin):
    search_fields = ['color']

class OrdersAdmin(ModelAdmin):
    search_fields = ['id', 'customer__email']  # استخدام 'id' بدلاً من 'number'
    list_display = ['id', 'customer_email', 'pdf_link']  # استخدام 'id' بدلاً من 'number'
    
    def customer_email(self, obj):
        return obj.customer.email
    
    # إضافة رابط لتوليد PDF في العمود الجديد
    def pdf_link(self, obj):
        url = reverse('admin-generate-pdf', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Generate receipt</a>', url)

    pdf_link.short_description = 'Generate receipt'

    # إضافة رابط عرض مخصص لتوليد PDF في الـ URLs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-pdf/<int:order_id>/', self.admin_site.admin_view(generate_order_pdf), name='admin-generate-pdf'),
        ]
        return custom_urls + urls
        
    

class CartModelAdmin(ModelAdmin):
    search_fields = ['user__email']

class CartItemAdmin(ModelAdmin):
    search_fields = ['product__name']

class ContactUsAdmin(ModelAdmin):
    search_fields = ['email', 'message']

class AddressAdmin(ModelAdmin):
    search_fields = ['user__email', 'address']

class SenderEmailAdmin(ModelAdmin):
    search_fields = ['email']

class CategrayAdmin(ModelAdmin):
    search_fields = ["name"]

class SocialMediAdmin(ModelAdmin):
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
