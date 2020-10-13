import uuid

from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import serializers, status
from rest_framework.utils import json

from .models import *


class Base64ImageField(serializers.ImageField):
    default_error_messages = {
        "invalid": "تصویر معتبر نیست.",
        "invalid_image": "تصویر معتبر نیست.",
        "required": "تصویر از قلم افتاده.",
        "missing": "تصویر از قلم افتاده.",
        "empty": "فایل تصویر خالی است.",
        "no_name": "نام تصویر نامعتبر است.",
    }

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    @staticmethod
    def get_file_extension(file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class CreateUserSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, allow_blank=False, allow_null=False, required=True)
    first_name = serializers.CharField(max_length=200, allow_blank=False, allow_null=False, required=True)
    last_name = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, required=False)
    password = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=False)

    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     user = User(**validated_data)  # other parameters
    #     user.email_subscription = 0
    #     user.sms_subscription = 0
    #     user.set_password(password)
    #     user.save()
    #     return user
    #
    # def update(self, instance, validated_data):
    #     # TODO Update User Serializer
    #     pass


class ChangePasswordSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, allow_blank=False, allow_null=False, required=True)
    password = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=False)


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.mobile')

    class Meta:
        model = User
        fields = ('user_id', 'first_name', 'last_name', 'mobile', 'is_staff', 'is_superuser', 'user')


########################
#  Product Serializers #
########################


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


class CategoryBase64Serializer(serializers.ModelSerializer):
    cover = Base64ImageField(max_length=None,
                             use_url=True,
                             allow_null=True,
                             error_messages={
                                "required": "کاور دسته از قلم افتاده.",
                                "missing": "کاور دسته از قلم افتاده.",
                                "invalid": "کاور دسته معتبر نیست.",
                                "invalid_image": "کاوردسته  معتبر نیست.",
                                "empty": "فایل کاور دسته خالی است.",
                                "no_name": "نام فایل کاور دسته نامعتبر است.",
                                "blank": "کاور دسته را وارد نمایید.",
                                "null": "کاور دسته را وارد نمایید."
                             })

    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {
            "title": {
                "error_messages": {
                        "blank": "عنوان دسته را وارد نمایید.",
                        "null": "عنوان دسته را وارد نمایید."
                     }
            },
        }


class ModelSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, error_messages={
                                "required": "تصویر مدل از قلم افتاده.",
                                "missing": "تصویر مدل از قلم افتاده.",
                                "invalid": "تصویر مدل معتبر نیست.",
                                "invalid_image": "تصویر مدل معتبر نیست.",
                                "empty": "فایل تصویر مدل خالی است.",
                                "no_name": "نام فایل تصویر مدل نامعتبر است.",
                                "blank": "تصویر مدل را وارد نمایید.",
                                "null": "تصویر مدل را وارد نمایید."
                             })

    class Meta:
        model = Model
        exclude = [
            'product',
        ]
        extra_kwargs = {
            "title": {
                "error_messages": {
                        "blank": "عنوان مدل را وارد نمایید.",
                        "null": "عنوان مدل را وارد نمایید."
                     }
            },
            "code": {
                "error_messages": {
                        "unique": "مدلی با این کد مدل قبلا ثبت شده.",
                        "blank": "کد مدل را وارد نمایید.",
                        "null": "کد مدل را وارد نمایید."
                     }
            },
            "price": {
                "error_messages": {
                    "blank": "قیمت مدل را وارد نمایید.",
                    "null": "قیمت مدل را وارد نمایید.",
                    "required": "قیمت مدل را وارد کنید.",
                    "invalid": "قیمت وارد شده درست نیست."
                }
            },
            "in_stock": {
                "error_messages": {
                    "blank": "موجودی مدل را وارد نمایید.",
                    "null": "موجودی مدل را وارد نمایید.",
                    "required": "موجودی مدل را وارد کنید.",
                    "invalid": "موجودی وارد شده درست نیست."
                }
            },
            "image": {
                "error_messages": {
                    "required": "تصویر مدل از قلم افتاده.",
                    "missing": "تصویر مدل از قلم افتاده.",
                    "invalid": "تصویر مدل معتبر نیست.",
                    "invalid_image": "تصویر مدل معتبر نیست.",
                    "empty": "فایل تصویر مدل خالی است.",
                }
            },
        }

    # prevent django from converting pk to object in nested serializers
    def to_internal_value(self, data):
        color_data = data.get("color")
        if isinstance(color_data, Color):  # if object is received
            data["color"] = color_data.pk  # change to its pk value
        obj = super(ModelSerializer, self).to_internal_value(data)
        return obj


class ProductSerializer(serializers.ModelSerializer):
    models = ModelSerializer(many=True)
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())

    main_image_errors = {
        "invalid": "تصویر اصلی معتبر نیست.",
        "invalid_image": "تصویر اصلی معتبر نیست.",
        "required": "تصویر اصلی از قلم افتاده.",
        "missing": "تصویر اصلی از قلم افتاده.",
        "empty": "فایل تصویر اصلی خالی است.",
        "no_name": "نام تصویر اصلی نامعتبر است.",
    }
    second_image_errors = {
        "invalid": "تصویر دوم معتبر نیست.",
        "invalid_image": "تصویر دوم معتبر نیست.",
        "required": "تصویر دوم از قلم افتاده.",
        "missing": "تصویر دوم از قلم افتاده.",
        "empty": "فایل تصویر دوم خالی است.",
        "no_name": "نام تصویر دوم نامعتبر است.",
    }
    size_image_errors = {
        "invalid": "تصویر راهنما معتبر نیست.",
        "invalid_image": "تصویر راهنما معتبر نیست.",
        "required": "تصویر راهنما از قلم افتاده.",
        "missing": "تصویر راهنما از قلم افتاده.",
        "empty": "فایل تصویر راهنما خالی است.",
        "no_name": "نام تصویر راهنما نامعتبر است.",
    }

    main_image = Base64ImageField(max_length=None, use_url=True, error_messages=main_image_errors)
    second_image = Base64ImageField(max_length=None, use_url=True, error_messages=second_image_errors)
    size_image = Base64ImageField(max_length=None, use_url=True, error_messages=size_image_errors)

    class Meta:
        model = Product
        extra_kwargs = {
            "title": {
                "error_messages": {
                        "blank": "عنوان محصول را وارد نمایید.",
                        "null": "عنوان محصول را وارد نمایید."
                     }
            },
            "code": {
                "error_messages": {
                        "blank": "کد محصول را وارد نمایید.",
                        "null": "کد محصول را وارد نمایید."
                     }
            },
        }
        exclude = (
            'likes',
            'tags',
            'auctions',
            'gifts',
        )

    # at least 1 model requried
    def validate_models(self, attrs):
        if len(attrs) == 0:
            raise serializers.ValidationError('حداقل یک مدل برای تعریف محصول لازم است.')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        models_validated_data = validated_data.pop('models')
        categories_validated_data = validated_data.pop('categories')

        product = Product.objects.create(**validated_data)

        # models
        for model in models_validated_data:
            model['product'] = product
            model_serializer = ModelSerializer(data=model)
            model_serializer.create(model)

        # categories
        product.categories.set(categories_validated_data)

        return product


class SendMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendMethod
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    cart = serializers.JSONField(write_only=True)

    class Meta:
        model = Order
        fields = ('order_id',
                  'user',
                  'order_status',
                  'tracking_code',
                  'phone',
                  'postal_code',
                  'postal_address',
                  'datetime',
                  'total_price',
                  'models',
                  'cart',  # includes models and quantities
                  'send_method',
                  )

    @transaction.atomic
    def create(self, validated_data):
        # validated_data
        cart = validated_data.pop('cart')
        validated_data.pop('tracking_code')  # to generate manually server-side
        send_method = validated_data.get('send_method')

        # Variables
        total_price = send_method.price

        # Create order
        order = Order.objects.create(**validated_data,
                                     send_method_price=send_method.price,
                                     )

        # Generate Unique tracking_code
        random_string = get_random_string(length=10, allowed_chars=''.join((string.ascii_uppercase, string.digits)))
        while True:  # unique check
            x = Order.objects.filter(tracking_code=random_string)
            if not x.exists():
                break
            else:
                random_string = get_random_string(length=10, allowed_chars=''.join((string.ascii_uppercase, string.digits)))
        order.tracking_code = random_string

        # Assign models to order
        for item in cart:
            model = Model.objects.get(pk=item['model'])
            quantity = item['quantity']

            # save new order
            new_order_model = OrderModel()
            new_order_model.order = order
            new_order_model.model = model
            new_order_model.price = model.price
            new_order_model.quantity = quantity
            new_order_model.save()

            # Decrease in_stock
            model.in_stock -= quantity
            model.save()

            # Add model price
            total_price += quantity * model.price

        # Set final total_price on order
        order.total_price = total_price

        # Insert order to database
        order.save()

        return order
