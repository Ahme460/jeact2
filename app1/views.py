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
            cart, created = CartModel.objects.get_or_create(customer=request.user)
            item, item_created = CartItem.objects.get_or_create(product_id=product_id, cart=cart)

            if not item_created:
                item.quantity += 1
                item.save()
            else:
                item.quantity = request.data.get('quantity', 1)
                item.save()

            return Response({"detail": "Item added to cart."}, status=status.HTTP_200_OK)
        except CartModel.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)








    @action(detail=False, methods=['delete'], url_path='remove-item/(?P<product_id>[^/.]+)')
    def remove_item(self, request, product_id=None):
        try:
            cart = CartModel.objects.get(customer=request.user)
            item = CartItem.objects.get(product__id=product_id, cart=cart)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartModel.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found in the cart."}, status=status.HTTP_404_NOT_FOUND)
    
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
                if not payment_url:
                    return Response({"error": "Failed to generate payment URL"}, status=status.HTTP_400_BAD_REQUEST)
                
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
