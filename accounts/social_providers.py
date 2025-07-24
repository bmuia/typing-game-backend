import urllib.parse
from django.conf import settings
import requests
from django.contrib.auth import get_user_model

# Get the custom User model (can be default or a custom user class)
User = get_user_model()

def google_login():
    """
    Initiates the Google OAuth2 login process.

    Constructs the URL that redirects the user to Google's authorization page.
    Includes required query parameters like client_id, redirect_uri, response_type,
    and scope (for email, profile, etc.).

    This function is called when the frontend wants to initiate login with Google.
    """
    url = 'https://accounts.google.com/o/oauth2/auth'

    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.REDIRECT_URI,  # The URL Google will redirect back to after login
        'response_type': 'code',                # Authorization code grant
        'scope': 'openid email profile',        # Permissions we're requesting
    }

    # Return the complete URL to redirect the user to Google's OAuth2 consent screen
    return f"{url}?{urllib.parse.urlencode(params)}"


def get_user_profile(access_token):
    """
    Fetches the user's profile info using the Google-provided access token.

    Calls the Google API endpoint to retrieve user details like email and first name.
    Uses this information to either retrieve an existing user or create a new one.

    Returns the User object or None if fetching fails.
    """
    headers = {
        'Authorization': f'Bearer {access_token}'  # Pass the token as Bearer token
    }
    url = 'https://www.googleapis.com/oauth2/v1/userinfo'  # Google API endpoint for user info

    user_profile_response = requests.get(url, headers=headers)
    user_info = user_profile_response.json()

    first_name = user_info.get('given_name')
    email = user_info.get('email')

    if not email:
        return None  # Email is required to identify/create a user

    # If user exists, return it; otherwise, create a new user with the provided email and first name
    user, created = User.objects.get_or_create(
        email=email,
        defaults={'first_name': first_name}
    )
    return user


def google_callback(code):
    """
    Handles the OAuth2 callback logic.

    Exchanges the authorization code (received from Google) for an access token.
    Then uses that token to fetch the user's profile and either create or retrieve the user.

    Returns the User object or None if the flow fails at any point.
    """
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
        return None  # Could not exchange code for token

    return get_user_profile(access_token)
