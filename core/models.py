from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, mobile, password=None, is_staff=False, is_active=True, is_admin=False):
        if not mobile:
            raise ValueError('Users must have a phone number.')

        user_obj = self.model(
            mobile=mobile,
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.is_active = is_active
        user_obj.is_admin = is_admin
        user_obj.email_subscribtion = False
        user_obj.sms_subscription = False
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, mobile, password=None, email=None):
        user = self.create_user(
            mobile=mobile,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)

    # role_id
    # method_id (az che ravershi ba goldiba ashna shodid?)
    # city_id

    first_name = models.CharField(max_length=200, verbose_name='First Name', blank=True, null=True)
    last_name = models.CharField(max_length=200, verbose_name='Last Name', blank=True, null=True)

    username = models.CharField(max_length=64, verbose_name='Username', blank=True, null=True)
    password = models.CharField(max_length=255, verbose_name='Password', blank=True, null=True)
    email = models.EmailField(verbose_name='Email Address')

    # mobile_regex = RegexValidator(regex=r'^\+?98?\d{9,14}$', message='Phone format is +98XXXXXXXXXX.')
    mobile = models.CharField(
        # validators=[mobile_regex],
        max_length=15,
        unique=True,
        verbose_name='Mobile Phone Number'
    )

    gender = [
        ('U', 'Unknown'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    email_subscribtion = models.BooleanField(verbose_name='Email Newsletter')
    sms_subscription = models.BooleanField(verbose_name='SMS Newsletter')

    # TODO addresses (NEW many to many relation)
    # phone = models.CharField(max_length=15, verbose_name='Reciever Phone Name')
    # postal_code = models.CharField(max_length=15, verbose_name='Receiver Postal Code')
    # postal_address = models.TextField(max_length=255, verbose_name='Reciever Postal Address')

    USERNAME_FIELD = 'mobile'
    # EMAIL_FIELD = 'email'
    # REQUIRED_FIELDS = []

    objects = UserManager()

    def get_full_name(self):
        return self.first_name + " " + self.last_name
