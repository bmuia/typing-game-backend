from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Custom manager to handle user creation logic
class CustomUserManager(BaseUserManager):

    # Method to create a regular user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')  # Ensure email is provided
        email = self.normalize_email(email)  # Normalize email (e.g., lowercase domain part)
        user = self.model(email=email, **extra_fields)  # Create user instance
        user.set_password(password)  # Hash and set the password
        user.save(using=self._db)  # Save the user to the database
        return user

    # Method to create a superuser (admin)
    def create_superuser(self, email, password=None, **extra_fields):
        # Set required superuser flags
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Validate required flags for superuser
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # Email as the unique identifier
    first_name = models.CharField(max_length=30, blank=True)  # Optional first name
    last_name = models.CharField(max_length=30, blank=True)   # Optional last name
    is_active = models.BooleanField(default=True)             # Indicates if account is active
    is_staff = models.BooleanField(default=False)             # Grants access to admin site
    date_joined = models.DateTimeField(auto_now_add=True)     # When the user registered

    objects = CustomUserManager()  # Use custom manager

    USERNAME_FIELD = 'email'       # Use email to log in
    REQUIRED_FIELDS = ['first_name']  # Required when creating superuser via CLI

    def __str__(self):
        return self.email  # Human-readable representation
