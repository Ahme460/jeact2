
from django.urls import path,include
from rest_framework.routers import DefaultRouter

from .views import *
router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('cart', CartViewSet)
router.register('contact_us',ContactUsViewSet)
urlpatterns = [
    path('sing/', RegisterAPIView.as_view(), name='sing up'),
    path('login/', login, name='login'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('request-reset-password/', RequestPasswordResetView.as_view(), name='request-reset-password'),
    path('reset-password/<uidb64>/<token>/', PasswordResetView.as_view(), name='reset-password'),
    path('api/', include(router.urls)),
    path('payment-callback/', PaymobCallbackView.as_view(), name='payment-callback'),
    path('categories/', CategoryViewSet.as_view(), name='category-list'),
    path("account_data/",DataUserViewSet.as_view(),name="my_data")
    
]







