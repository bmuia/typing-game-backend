# ----------------------------- VIEWS ----------------------------- #

from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .social_providers import google_login, google_callback
import urllib.parse


class GoogleLogin(APIView):
    """
    API endpoint to initiate the Google login.

    Redirects the user to Google's OAuth2 consent screen.
    The frontend should call this endpoint when the user clicks "Login with Google".
    """
    def get(self, request):
        url = google_login()
        return redirect(url)


class GoogleCallback(APIView):
    """
    API endpoint to handle the OAuth2 callback after Google authentication.

    This is the redirect_uri specified in the original Google OAuth request.
    It receives the authorization code, fetches the user profile,
    creates (or gets) the user, and issues JWT access and refresh tokens.

    The tokens are returned to the frontend via a query string redirect.
    """
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            # No code in the callback, redirect back to frontend with error
            return redirect('http://localhost:3000/oauth/callback?error=missing_code')

        # Exchange code for access token, then get or create user
        user = google_callback(code)
        if not user:
            return redirect('http://localhost:3000/oauth/callback?error=auth_failed')

        # Generate JWT tokens using SimpleJWT
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Pass the tokens back to the frontend in query params
        query_params = urllib.parse.urlencode({
            'access': str(access),
            'refresh': str(refresh),
        })

        return redirect(f"http://localhost:3000/oauth/callback?{query_params}")
