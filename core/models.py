import os

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.http import JsonResponse
from rest_framework.fields import JSONField

from api import settings


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, mobile, password=None, is_staff=False, is_active=True, is_admin=False):
        if not mobile:
            raise ValueError('Users must have a mobile number.')

        try:
            User.objects.get(mobile=mobile)
            return JsonResponse({
                'type': 'error',
                'message': 'کاربری با این شماره قبلا ثبت شده.'
            }, status=406)
        except User.DoesNotExist:
            user_obj = self.model(
                mobile=mobile,
            )
            user_obj.set_password(password)
            user_obj.staff = is_staff
            user_obj.is_active = is_active
            user_obj.is_admin = is_admin
            user_obj.email_subscription = False
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

    mobile = models.CharField(
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

    email_subscription = models.BooleanField(verbose_name='Email Newsletter', blank=True, null=True)
    sms_subscription = models.BooleanField(verbose_name='SMS Newsletter', blank=True, null=True)

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


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag = models.CharField(max_length=255, verbose_name='Tag Text', blank=False, null=False)

    def __str__(self):
        return self.tag


class Auction(models.Model):
    auction_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='Auction Title', blank=True, null=True)
    percent = models.PositiveIntegerField(verbose_name='Off Percentage', blank=False, null=False)
    start_date = models.DateTimeField(verbose_name='Start Time/Date', blank=False, null=False)
    end_date = models.DateTimeField(verbose_name='Start Time/Date', blank=False, null=False)
    cover = models.ImageField(upload_to='images/auction/'+auction_id.__str__()+'/', blank=True, null=True)

    def __str__(self):
        return self.title


class Gift(models.Model):
    gift_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='Gift Title', blank=False, null=False)
    cover = models.ImageField(upload_to='images/gift/'+gift_id.__str__()+'/', blank=True, null=True)

    def __str__(self):
        return self.title


def get_upload_path_brands(instance, filename):
    return os.path.join(settings.MEDIA_ROOT, 'images/brands/', instance.name, filename)


class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Persian Name', blank=False, null=False)
    english_name = models.CharField(max_length=255, verbose_name='English Name', blank=True, null=True)
    image = models.ImageField(upload_to=get_upload_path_brands, blank=True, null=True)

    def __str__(self):
        return self.name


class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=255, verbose_name='Status Title', blank=False, null=False)

    class Meta:
        verbose_name_plural = "Statuses"

    def __str__(self):
        return self.label


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)

    title = models.CharField(max_length=255, verbose_name='Title', blank=False, null=False)
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    code = models.CharField(max_length=32, verbose_name='Product Code', blank=False, null=False)
    discount = models.PositiveSmallIntegerField(verbose_name='Product Discount', blank=False, null=False)
    free_send = models.BooleanField(verbose_name='Free Send', blank=False, null=False)
    main_image = models.ImageField(upload_to='images/product/'+product_id.__str__()+'/', blank=False, null=False)
    second_image = models.ImageField(upload_to='images/product/'+product_id.__str__()+'/', blank=True, null=True)
    size_image = models.ImageField(upload_to='images/product/'+product_id.__str__()+'/', blank=True, null=True)

    params = JSONField("Parameters", default={})  # Product parameters
    relatives = JSONField("Parameters", default={})  # Relative Products

    likes = models.PositiveIntegerField(verbose_name='Product Like Count', blank=False, null=False)

    # One-to-many relations
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.SET_NULL, blank=True, null=True)
    status = models.ForeignKey(Status, related_name='products', on_delete=models.PROTECT, blank=True)

    # Many-to-many relations
    tags = models.ManyToManyField('Tag', related_name='products', blank=True)
    auctions = models.ManyToManyField('Auction', related_name='products', blank=True)
    gifts = models.ManyToManyField('Gift', related_name='products', blank=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Category Title', blank=False, null=False)
    category_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT)
    cover = models.ImageField(upload_to='images/category/'+category_id.__str__()+'/', blank=True, null=True)
    products = models.ManyToManyField(Product, related_name='categories', through='ProductCategory')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


class ParameterCategory(models.Model):
    parameter_category_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='Parameter Category Title', blank=False, null=False)
    compare = models.BooleanField(verbose_name='Comparable', blank=False, null=False)

    class Meta:
        verbose_name_plural = "Parameter categories"


class ProductCategory(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    main_category = models.BooleanField(verbose_name='Main Category', blank=True, null=True, default=False)
    parameter_categories = models.ManyToManyField(ParameterCategory, related_name='product_categories')

    class Meta:
        verbose_name_plural = "Product categories"


class Parameter(models.Model):
    PARAMETER_TYPE_CHOICES = [
        ('ST', 'Short Text'),
        ('LT', 'Long Text'),
        ('MO', 'Multiple Options'),
        ('SO', 'Single Option'),
    ]

    parameter_id = models.AutoField(primary_key=True)
    parameter_category_id = models.ForeignKey(ParameterCategory, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    parameter_type = models.CharField(
        max_length=3,
        choices=PARAMETER_TYPE_CHOICES,
        default='ST',
    )
    name = models.CharField(max_length=255, verbose_name='Parameter Name', blank=False, null=False)


class Color(models.Model):
    color_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Color Name', blank=False, null=False)
    hex = models.CharField(max_length=32, verbose_name='HEX Code', blank=False, null=False)


class Model(models.Model):
    model_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='models', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name='models', on_delete=models.PROTECT)
    code = models.CharField(max_length=32, verbose_name='Model Code', blank=False, null=False)
    title = models.CharField(max_length=255, verbose_name='Model Name', blank=False, null=False)
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    price = models.PositiveIntegerField(verbose_name='Price', blank=False, null=False)
    in_stock = models.PositiveSmallIntegerField(verbose_name='# In Stock', blank=False, null=False)
    image = models.ImageField(upload_to='images/model/'+model_id.__str__()+'/', blank=False, null=False)
    is_active = models.BooleanField(verbose_name='Activation Status', blank=True, null=True)


