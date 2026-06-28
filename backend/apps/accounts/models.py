import random
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUPER_ADMIN')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        OWNER = 'OWNER', 'Owner'
        MANAGER = 'MANAGER', 'Manager'
        DRIVER = 'DRIVER', 'Driver'

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.DRIVER)
    
    # OTP fields for driver login
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def generate_otp(self):
        self.otp_code = f"{random.randint(100000, 999999)}"
        self.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        self.save(update_fields=['otp_code', 'otp_expiry'])
        return self.otp_code

    def verify_otp(self, code):
        if self.otp_code == code and self.otp_expiry and self.otp_expiry > timezone.now():
            self.otp_code = None
            self.otp_expiry = None
            self.save(update_fields=['otp_code', 'otp_expiry'])
            return True
        return False

    def __str__(self):
        return f"{self.email} ({self.role})"
