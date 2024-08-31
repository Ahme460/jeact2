from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from .models import *
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.password_validation import validate_password


User = get_user_model()




class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password])
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def save(self):
        try:
            uid = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid uidb64 or token.")
        
        if not default_token_generator.check_token(user, self.validated_data['token']):
            raise serializers.ValidationError("Invalid token or token has expired.")
        
        user.set_password(self.validated_data['new_password'])
        user.save()














class SingUpSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)  # معالجة اسم الدولة بدلاً من المعرف

    class Meta:
        model = User
        fields = ('first_name', 'username', 'email', 'password', 'password2', 'country', 'currence')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if len(data['password']) < 8:
            raise serializers.ValidationError("password is very weak ")
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        country_name = validated_data.pop('country')
        try:
            country = Country.objects.get(name=country_name)
        except Country.DoesNotExist:
            raise serializers.ValidationError({"country": "Country not found."})
        user = User.objects.create_user(**validated_data, country=country)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

class ColorSer(serializers.ModelSerializer):
    class Meta:
        model = ColorsModel
        exclude = ['product']

class SizesSer(serializers.ModelSerializer):
    class Meta:
        model = SizesModel
        exclude = ['product']



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    colors = ColorSer(many=True, read_only=True)
    sizes = SizesSer(many=True, read_only=True)
    converted_price = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Products
        fields = "__all__"

    def get_converted_price(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            user_currency = request.user.currence
            return obj.convert_price(user_currency)
        return obj.price

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                data['user'] = user
            else:
                raise AuthenticationFailed('Invalid login credentials')
        else:
            raise AuthenticationFailed('Must include "email" and "password"')
        return data

class ProductSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('details', 'name', 'price')

class CartItemSerializer(serializers.ModelSerializer):
    converted_price = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_photo = serializers.SerializerMethodField()
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'quantity', 'size', 'color', 'date_added', 
            'converted_price', 'product_name', 'product_photo', 'product_details'
        ]
    def get_converted_price(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            user_currency = request.user.currence
            return obj.product.convert_price(user_currency)
        return obj.product.price

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_photo(self, obj):
        request = self.context.get('request', None)
        if request:
            return request.build_absolute_uri(obj.product.photo.url)
        return obj.product.photo.url

    def get_product_details(self, obj):
        return obj.product.details

    def create(self, validated_data):
        cart, created = CartModel.objects.get_or_create(customer=self.context['request'].user)
        return CartItem.objects.create(cart=cart, **validated_data)
    
class CartSer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    products=ProductSerializer(many=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    
   
    class Meta:
        model = CartModel
        fields = "__all__"
        


    #def get_total_price(self, obj):
     #   request = self.context.get('request', None)
      #  if request and request.user.is_authenticated:
       #     user_currency = request.user.currence
        #    total = sum(item.product.convert_price(user_currency) * item.quantity for item in obj.items.all())
         #   return total
        #return sum(item.product.discount * item.quantity for item in obj.items.all())

    def create(self, validated_data):
        cart, created = CartModel.objects.get_or_create(customer=self.context['request'].user)
        return cart

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = categories
        fields = '__all__'
        
        
        
class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorsModel
        fields = ['color']
        
        
        
        
class Brovince_ser(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'
        
        
        
      
        
class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social_media
        fields = '__all__'


  
        
class Wep(serializers.ModelSerializer):
    class Meta:
        model = Text_pic_wep  # Corrected typo here
        fields = '__all__' 

class CustomerUserUpdateSerializer(serializers.ModelSerializer):
    country = serializers.CharField()

    class Meta:
        model = Customer_user
        fields = ['country', 'currence']

    def validate_country(self, value):
        try:
            country = Country.objects.get(name=value)
            return country.id
        except Country.DoesNotExist:
            raise serializers.ValidationError("Country not found.")

    def update(self, instance, validated_data):
        country_id = validated_data.pop('country', None)
        if country_id:
            instance.country_id = country_id
        return super().update(instance, validated_data)
        

class ProductSerializerwish(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['name', 'price', 'categray', 'about_product', 'photo', 'sale_status', 'details', 'discount', 'is_featured']

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'added_at']
        read_only_fields = ['user', 'added_at']
        
        

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizesModel
        fields = ['size', 'descrtions_size_fit', 'count']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorsModel
        fields = ['color']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    sizes = SizeSerializer(many=True, read_only=True)
    colors = ColorSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Products
        fields = '__all__'