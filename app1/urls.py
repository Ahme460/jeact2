
from django.urls import path,include
from rest_framework.routers import DefaultRouter

from .views import *
router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('cart', CartViewSet)
router.register('contact_us',ContactUsViewSet)
urlpatterns = [
    path('sing/', register, name='sing up'),
    path('login/', login, name='login'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('request-reset-password/', RequestPasswordResetView, name='request-reset-password'),
    path('reset-password/<uidb64>/<token>/', PasswordResetView, name='reset-password'),
    path('api/', include(router.urls)),
    path('payment-callback/', PaymobCallbackView.as_view(), name='payment-callback'),
]







