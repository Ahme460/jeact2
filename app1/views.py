from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import SingUpSerializer
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from rest_framework.viewsets import ModelViewSet
import os
from django.shortcuts import redirect
import importlib
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .tasks import *
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
import time
from django.db.models import Q
from .models import *
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .pymob import pay
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from .serializers import PasswordResetRequestSerializer, PasswordResetSerializer
from django.shortcuts import get_object_or_404
from .exchange_price import exchange
from.class_send_email import SenderMail
from.order import send_order_mail
User = get_user_model()
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            countries = Country.objects.all()
            country_list = [{'id': country.id, 'name': country.name} for country in countries]
            return Response(country_list, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"field": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        serializer = SingUpSerializer(data=data)
        if serializer.is_valid():
            if not User.objects.filter(username=data['username']).exists():
                user = serializer.save()
                # استخدام send_mail بدلاً من EmailMessage
                # send_mail(
                #     subject="Permit to Work",
                #     message="Welcome",
                #     from_email='info@bantayga.wtf',
                #     recipient_list=[user.email],
                #     fail_silently=False,
                # )
                SenderMail(
                    subject="welcome to BANTAYGA",
                    content= """
                    Welcome to Bantyaga!

We're thrilled to have you join our community! We hope you have a fantastic experience filled with valuable insights and opportunities. You'll find a wealth of resources and information to help you achieve your goals.

If you have any questions or need assistance, don't hesitate to reach out to us. We're here to support you.

Thank you for joining, and we look forward to being part of your journey!
""",
tem='welcome_email.html'

                    
                ).send_mail(emails=data['email'])
                
                return Response(
                    {'details': 'Your account registered successfully!'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': 'This email already exists!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

# @api_view(['GET'])
# def product_list_view(request):
#     products = Products.objects.all()
#     if "color" in request.query_params:
#         colors = request.query_params['color']
#         products = products.filter(color__color__in=colors)
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)
class RequestPasswordResetView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = PasswordResetSerializer(data={**request.data, 'uidb64': uidb64, 'token': token})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# @api_view(['GET'])
# def product_detail(request, pk):
#     try:
#         product = Products.objects.get(pk=pk)
#     except Products.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#     serializer = ProductSerializer_detal(product)
#     return Response(serializer.data)


class CartViewSet(ModelViewSet):
    queryset = CartModel.objects.all()
    serializer_class = CartSer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CartItemSerializer
        return CartSer

    def get_queryset(self):
        return CartModel.objects.filter(customer=self.request.user)

    @action(detail=False, methods=['post'], url_path='add-item/(?P<product_id>[^/.]+)')
    def add_item(self, request, product_id=None):
        try:
        # الحصول أو إنشاء عربة التسوق الخاصة بالمستخدم
            cart, created = CartModel.objects.get_or_create(customer=request.user)
            
            # محاولة الحصول على المنتج
            product = get_object_or_404(Products, id=product_id)
            
            # الحصول على اللون والحجم المرسلين
            color = request.data.get('color')
            size = request.data.get('size')
            quantity = int(request.data.get('quantity', 1))  # تأكد من تحويل الكمية إلى عدد صحيح

            # التأكد من صحة الحجم واللون إذا تم إرسالهما
            if color:
                color_obj = get_object_or_404(ColorsModel, product=product, color=color)
            if size:
                size_obj = get_object_or_404(SizesModel, product=product, size=size)

            # البحث عن عنصر CartItem أو إنشائه إذا لم يكن موجودًا بالفعل
            item, item_created = CartItem.objects.get_or_create(
                product=product, 
                cart=cart,
                defaults={
                    'quantity': quantity,
                    'color': color if color else 'none',
                    'size': size if size else 'none'
                }
            )

            # إذا كان العنصر موجودًا بالفعل، تحديث الكمية
            if not item_created:
                item.quantity += quantity
                item.color = color if color else item.color
                item.size = size if size else item.size
                item.save()

            return Response({"detail": "Item added to cart."}, status=status.HTTP_200_OK)
        
        except ValueError:
            return Response({"detail": "Invalid quantity value."}, status=status.HTTP_400_BAD_REQUEST)
        except Products.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except ColorsModel.DoesNotExist:
            return Response({"detail": f"Color '{color}' not available for this product."}, status=status.HTTP_404_NOT_FOUND)
        except SizesModel.DoesNotExist:
            return Response({"detail": f"Size '{size}' not available for this product."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['delete'], url_path='remove-item/(?P<product_id>[^/.]+)')
    def remove_item(self, request, product_id=None):
        try:
            cart = CartModel.objects.get(customer=request.user)
            # استخدام filter بدلاً من get للتعامل مع احتمالية وجود أكثر من عنصر
            items = CartItem.objects.filter(product__id=product_id, cart=cart)
            
            # حذف كل العناصر المطابقة
            if items.exists():
                items.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"detail": "Item not found in the cart."}, status=status.HTTP_404_NOT_FOUND)
                
        except CartModel.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

    
class IncreaseQuantity(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        try:
            product_id = request.data.get("product_id")
            quantity = request.data.get("quantity")

            # التحقق من أن quantity عدد صحيح
            if not isinstance(quantity, int):
                return Response({
                    "error": "Quantity must be an integer"
                }, status=status.HTTP_400_BAD_REQUEST)

            # البحث عن الـ Cart الخاصة بالمستخدم
            cart = get_object_or_404(CartModel, customer=request.user)

            # البحث عن الـ CartItem الخاصة بالمنتج داخل السلة
            product_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
            # زيادة الكمية

            product_item.quantity = quantity
            product_item.save()


            return Response({
                "message": "Quantity increased successfully.",
                "new_quantity": product_item.quantity
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
    
    
    
#@api_view(['GET'])
#def user_cart(request, user_id):
 ##  total_price = 0
   # for item in cart_items:
    #    total_price += item.product.price * item.quantity
    #serializer = CartItemSerializer(cart_items, many=True)
    #data = serializer.data
    #for i in range(len(data)):
     #   data[i]['total_price'] = cart_items[i].product.price * cart_items[i].quantity
    #return Response(data)

#@api_view(['DELETE'])
#def delete_cart_item(request, cart_item_id):
 #   try:
  #      cart_item = CartItem.objects.get(pk=cart_item_id)
   #3 except CartItem.DoesNotExist:
    #    return Response(status=status.HTTP_404_NOT_FOUND)

    #cart_item.delete()
    #return Response(status=status.HTTP_204_NO_CONTENT)
class ProductViewSet(ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    #permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    #filterset_fields = ['colors__color', 'sizes__size']
    #search_fields = ['name', 'details']
    filterset_fields = ['colors__color', 'sizes__size', 'categray__id', 'categray__name']
    search_fields = ['name', 'details', 'categray__name', 'categray__id']
    ordering_fields = ['price', 'id']
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class CategoryViewSet(APIView):
    def get(self, request):
        # Get the 'id' parameter from the query parameters
        category_id = request.query_params.get('id', None)
        
        # Validate and filter categories based on the 'id' parameter if it exists
        if category_id is not None:
            try:
                category_id = int(category_id)
                categories_filtered = categories.objects.filter(Q(id=category_id))
            except ValueError:
                return Response(
                    {"error": "Invalid 'id' parameter. It should be a number."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            categories_filtered = categories.objects.all()
        
        serializer = CategorySerializer(categories_filtered, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class ContactUsViewSet(ModelViewSet):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    
    
    
class AddressView(APIView):

     def post(self, request):
        try:
            user = request.user
            data = request.data
            data['user'] = user.id
            if user.country is not None:
                data['country'] = user.country.name  # الحصول على اسم الدولة كنص
            else:
                return Response({"error": "User does not have an assigned country."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = AddressSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": "done"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(user=user)

    def perform_create(self, serializer):
        address = serializer.save(user=self.request.user)
         
        # Get the province details
        province = address.province
        province_serializer = ProvinceSerializer(province)

        return Response({
            'address': serializer.data,
            'province': province_serializer.data,
            'delivery_price': province.delivery_price
        }, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        user_country = self.request.user.country
        provinces = Province.objects.filter(country__name=user_country)
        province_serializer = ProvinceSerializer(provinces, many=True)
        return Response(province_serializer.data)
    
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            cart = CartModel.objects.get(customer=user)
            address = Address.objects.filter(user=user).order_by('-id').first()
            #address = Address.objects.get(user=user)
            province = address.province
            delivery_price = province.delivery_price

            if delivery_price:
                total_price = cart.total_price + delivery_price
                total_price= exchange(int(total_price))
                api_key="ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RjME16QXhMQ0p1WVcxbElqb2lNVGN5TVRRNU5EYzROaTQwT0RjeU5qWWlmUS5aY1pMNUNVWTdSRld1S3d6eEhwLXlOS3F0RWUxVEhyZmh5TTdyWmplc1pGU3FjZVZWalptZWRudEZSdHh1MEk1M29sQWZIQkd6dVRLT3lvUWpjTEo5dw=="
                #api_key="ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1Rnek5URTRMQ0p1WVcxbElqb2lhVzVwZEdsaGJDSjkud1dHbXNsUlBsYVRXWVRkU2h6dXVfbFJhTkxiMTVoVUNBOFFJRDNYLUNqby12RjVlQ3Jkall0NS1ydzVRb01fOHczMmhXM3hYNVdLRmNweTg3aTlaU2c="
                #api_key="ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RjME16QXhMQ0p1WVcxbElqb2lhVzVwZEdsaGJDSjkuR2duRjJjU0pnRThsbVpqRnVGMWdPTHlzaFdlSnpSOVBJTDFkT1RBQ3B0Z3JqckxnUmo5WU43MHZqOGlGYUdVQzZmUm5mQ2tQWDZUbHBkcUVFX3J6NUE="
                #api_key ="ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2TnpReU5qWTFMQ0p1WVcxbElqb2lhVzVwZEdsaGJDSjkuR29Qem90Q1AyRDZrSHRXS2JKUHNNMG9rU1piNlFVbHBWOEdsZFpVOF9iSURnekNQb1FtN1hvdW9CMi04YzNmOG9mVlJJYm82TXhPX0g5RmZsR1U0N0E="
                #api_key="ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1Rnek5URTRMQ0p1WVcxbElqb2lhVzVwZEdsaGJDSjkud1dHbXNsUlBsYVRXWVRkU2h6dXVfbFJhTkxiMTVoVUNBOFFJRDNYLUNqby12RjVlQ3Jkall0NS1ydzVRb01fOHczMmhXM3hYNVdLRmNweTg3aTlaU2c="
                #"ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RjME16QXhMQ0p1WVcxbElqb2lhVzVwZEdsaGJDSjkuR2duRjJjU0pnRThsbVpqRnVGMWdPTHlzaFdlSnpSOVBJTDFkT1RBQ3B0Z3JqckxnUmo5WU43MHZqOGlGYUdVQzZmUm5mQ2tQWDZUbHBkcUVFX3J6NUE=" 
                payment_url = pay(api_key, total_price, user)
                #if not payment_url:
                    #return Response({"error": "Failed to generate payment URL"}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No delivery price for this province"}, status=status.HTTP_400_BAD_REQUEST)
        except CartModel.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class PaymobCallbackView(APIView):
    def post(self, request):
        try:
            data = request.data
            payment_status = data.get('success', False)
            transaction_id = data.get('id', None)
            user_id = data.get('order', {}).get('merchant_order_id', None)

            if payment_status:
                user = Customer_user.objects.get(id=user_id)
                cart = get_object_or_404(CartModel, customer=user)
                address = Address.objects.get(user=user)
                
                order_details = "\n".join([f"{item.quantity} x {item.product.name} ({item.size}, {item.color})" for item in cart.items.all()])

                order = Orders.objects.create(
                    order=order_details,
                    customer=user,
                    phone_user=address.phone,
                    email=user.email,
                    location=address.location
                )

                #cart.items.all().delete()
                SenderMail(
                    subject="details your order",
                    content=order_details,
                    tem='welcome_email.html'
                    
                    
                ).send_mail(emails=user.email)
                
                cart.delete()

                return Response({'message': 'Payment successful and order created'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class DataUserViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class Get_color(APIView):
    def get(self,request):
        try:    
            colors=ColorsModel.objects.all()
            serializer=ColorSerializer(colors,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
        
        
        
class Brovicevew(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            country = user.country
            if country is not None:
                provinces = Province.objects.filter(country=country)
                serializer = Brovince_ser(provinces, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User does not have an assigned country."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        try:
            province_id = request.query_params.get('id', None)
            if province_id is not None:
                province_id = int(province_id)
                province = Province.objects.filter(Q(id=province_id)).first()
                if province:
                    delivery_price = province.delivery_price
                    return Response({"price": delivery_price}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Province not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Province ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid Province ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            
class SocialMed(APIView):
    def get(self, request):
        try:
            data = Social_media.objects.all()
            serializer = SocialSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class Wep_site(APIView):
    def get(self,request):
        try:
            data=Text_pic_wep.objects.all().first()
            serializer=Wep(data)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"eroot":str(e)},status=status.HTTP_400_BAD_REQUEST)
        
class CustomerUserUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomerUserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
    
    
class WishlistAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wishlists = Wishlist.objects.filter(user=request.user)
        if not wishlists.exists():
            return Response({"message": "No wishlist items found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WishlistSerializer(wishlists, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if created:
            return Response({"message": "Product added to wishlist"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Product already in wishlist"}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        wishlist = Wishlist.objects.filter(user=request.user, product_id=product_id)
        if wishlist.exists():
            wishlist.delete()
            return Response({"message": "Product removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "Product not found in wishlist"}, status=status.HTTP_404_NOT_FOUND)

class GetFeaturedProductsAPIView(APIView):

    def get(self, request):
        # جلب أول خمس منتجات مميزة
        featured_products = Products.objects.filter(is_featured=True)[:5]
        # عمل Serialize للمنتجات
        serializer = ProductSerializer(featured_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

class Create_order_Payment_upon_receipt(APIView):
    
    def post(self, request):
        user = request.user
        data = request.data
        try:
            # الحصول على سلة التسوق المرتبطة بالمستخدم
            cart = CartModel.objects.get(customer=user)
            cart_items = cart.items.all()

            # تجميع نص الطلب
            text_order = []
            text_order_str = ''
            if len(cart_items)==0:
                return Response({
                    "opps":"no product in card please add items first"
                    
                },status=status.HTTP_400_BAD_REQUEST)
                

            # إضافة كل عنصر في السلة إلى النص
            for i in cart_items:
                # تحويل المعلومات إلى نصوص مفهومة
                text_order.append(f"Product: {i.product.name}, Quantity: {i.quantity}, Size: {i.size}, Color: {i.color}")

            # تحويل القائمة إلى سلسلة نصية مع فواصل الأسطر
            text_order_str = '\n'.join(text_order)

            dic_list=[]
            for j in cart_items:
                total=j.quantity*j.product.price
                dic_list.append({
                    "product": j.product.name,
                    "quantity": j.quantity,
                    "price": j.product.price,
                    "aggregate": total
                })
                



            # إعداد البيانات لطلب الشراء
            data['customer'] = user.id  # تحويل المستخدم إلى معرف (ID)
            data['order'] = text_order_str
            data['total'] = float(cart.total_price)
            
            # استخدام السيريالايزر للتحقق من صحة البيانات وحفظها
            serializer = Payment_upon_receipt(data=data)

            if serializer.is_valid():
                serializer.save()
                cart.delete()
                send_order_mail(user=user,list=dic_list)
                return Response({"order": "done"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except CartModel.DoesNotExist:
            return Response({"error": "Cart not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        
        
    
    
    

class ApplyDiscountCodeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)
        try:
            cart = request.user.cart
            discount_code = DiscountCode.objects.get(code=code, active=True)

            # Check if the discount code is valid
            if not discount_code.is_valid():
                return Response({
                    "error": "The discount code is not valid."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Apply the discount code to the cart
            cart.discount_code = discount_code
            cart.save()

            return Response({
                "total_price_after_discount": cart.total_price
            }, status=status.HTTP_200_OK)
        except DiscountCode.DoesNotExist:
            return Response({
                "error": "Invalid or inactive discount code."
            }, status=status.HTTP_400_BAD_REQUEST)
        except CartModel.DoesNotExist:
            return Response({
                "error": "Cart does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)





class CreatePaymentIntention(APIView):
    def post(self, request):
        # Get user data (e.g., from request or your database)
        user = request.user

        # Define the payment intention request payload
        payload = {
            "amount": request.data.get("amount"),
            "currency": "EGP",
            "expiration": 5800,
            "payment_methods": [
                12, "card"
            ],
            "items": [
                {
                    "name": "Item name 1",
                    "amount": request.data.get("amount"),
                    "description": "Watch",
                    "quantity": 1
                }
            ],
            "billing_data": {
                "apartment": "6",
                "first_name": user.first_name,
                "last_name": user.last_name,
                "street": "938, Al-Jadeed Bldg",
                "building": "939",
                "phone_number": "01234956432",
                "country": "EG",
                "email": user.email,
                "floor": "1",
                "state": "Alkhuwair"
            },
            "special_reference": "ABCDE8121",
            "customer": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "extras": {
                    "re": "22"
                }
            },
            "extras": {
                "ee": 22
            }
        }

        # Set headers
        headers = {
            'Authorization': 'ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RjME16QXhMQ0p1WVcxbElqb2lNVGN5TVRRNU5EYzROaTQwT0RjeU5qWWlmUS5aY1pMNUNVWTdSRld1S3d6eEhwLXlOS3F0RWUxVEhyZmh5TTdyWmplc1pGU3FjZVZWalptZWRudEZSdHh1MEk1M29sQWZIQkd6dVRLT3lvUWpjTEo5dw==',
            'Content-Type': 'application/json'
        }

        # Send request to Paymob API
        response = requests.post('https://accept.paymob.com/v1/intention/', json=payload, headers=headers)

        if response.status_code == 201:
            # Handle the response
            return Response(response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)



class NewsletterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = NewsletterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data['email']
            SenderMail(
                    subject="welcome to BANTAYGA",
                    content= """
                    Welcome to Bantyaga!

We're thrilled to have you join our community! We hope you have a fantastic experience filled with valuable insights and opportunities. You'll find a wealth of resources and information to help you achieve your goals.

If you have any questions or need assistance, don't hesitate to reach out to us. We're here to support you.

Thank you for joining, and we look forward to being part of your journey!
""",
tem='welcome_email.html'

                    
                ).send_mail(emails=email)
            return Response({"message": "Email saved successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone
from datetime import timedelta
# دالة لتوليد PDF
from weasyprint import HTML

def generate_order_pdf(request, order_id):
    # استرجاع الطلب بناءً على ID
    order = Orders.objects.get(id=order_id)
    current_time = timezone.now()
    time_after_7days = current_time + timedelta(days=7)

    # تجهيز الـ template الخاصة بالـ PDF
    template = get_template('order_pdf_template.html')
    context = {
        'order': order,
        'time_now': current_time,
        'time_after_7days': time_after_7days,
    }
    html = template.render(context)

    # إنشاء الاستجابة كـ PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}.pdf"'

    # تحويل HTML إلى PDF وكتابته إلى الاستجابة
    HTML(string=html).write_pdf(response)

    return response