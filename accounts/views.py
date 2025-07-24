from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .social_providers import google_login, google_callback
import urllib.parse


class GoogleLogin(APIView):
    def get(self, request):
        url = google_login()
        return redirect(url)


class GoogleCallback(APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return redirect('http://localhost:3000/oauth/callback?error=missing_code')

        user = google_callback(code)
        if not user:
            return redirect('http://localhost:3000/oauth/callback?error=auth_failed')

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        query_params = urllib.parse.urlencode({
            'access': str(access),
            'refresh': str(refresh),
        })

        return redirect(f"http://localhost:3000/oauth/callback?{query_params}")
