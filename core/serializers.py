from rest_framework import serializers, status

from core.utils import unique_order_id_generator
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


class ModelSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Model
        # fields = '__all__'
        exclude = [
            'product',
            # 'image',
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
                    "required": "لطفا قیمت مدل را وارد کنید.",
                    "invalid": "قیمت وارد شده درست نیست."
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


class ModelOfOrderSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Model
        # fields = '__all__'
        exclude = [
            'product',
            # 'image',
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
                    "required": "لطفا قیمت مدل را وارد کنید.",
                    "invalid": "قیمت وارد شده درست نیست."
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


class ProductSerializer(serializers.ModelSerializer):
    models = ModelSerializer(many=True)

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
                        "unique": "محصولی با این کد محصول قبلا ثبت شده.",
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

    def create(self, validated_data):
        model_validated_data = validated_data.pop('models')
        product = Product.objects.create(**validated_data)
        model_serializer = self.fields['models']

        for model in model_validated_data:
            model['product'] = product

        model_serializer.create(model_validated_data)
        return product


class OrderSerializer(serializers.ModelSerializer):
    models = serializers.PrimaryKeyRelatedField(many=True, queryset=Model.objects.all())

    class Meta:
        model = Order
        fields = '__all__'
        # exclude = ('tracking_code',)

    def create(self, validated_data):
        validated_data.pop('tracking_code')  # use default
        rec_models = validated_data.pop('models')
        order = Order.objects.create(**validated_data)
        order.tracking_code = uuid.uuid4().hex[:8].upper()
        order.save()
        order.models.set(rec_models)
        return order
