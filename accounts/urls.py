from django.urls import path
from .views import GoogleLogin,GoogleCallback

urlpatterns = [
    path('google/login/', GoogleLogin.as_view(), name='google-login'),
    path('google/callback/', GoogleCallback.as_view(), name='google-callback')
]
