import urllib.parse
from django.conf import settings
import requests
from django.contrib.auth import get_user_model

User = get_user_model()

def google_login():
    url = 'https://accounts.google.com/o/oauth2/auth'

    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
    }

    return f"{url}?{urllib.parse.urlencode(params)}"


def get_user_profile(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    url = 'https://www.googleapis.com/oauth2/v1/userinfo'

    user_profile_response = requests.get(url, headers=headers)
    user_info = user_profile_response.json()

    first_name = user_info.get('given_name')
    email = user_info.get('email')

    if not email:
        return None

    # Create or get user
    user, created = User.objects.get_or_create(
        email=email,
        defaults={'first_name': first_name}
    )
    return user


def google_callback(code):
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.REDIRECT_URI,
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=token_data)
    response_json = response.json()

    access_token = response_json.get('access_token')
    if not access_token:
        return None

    return get_user_profile(access_token)
