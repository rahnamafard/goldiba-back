from django.db import IntegrityError
import random
import string
import os

from django.utils.encoding import force_text
from rest_framework import status
from rest_framework.exceptions import APIException

from api import settings


# get directories for upload images
def get_upload_path_brands(instance, filename):
    return os.path.join(settings.MEDIA_ROOT, 'images/brands/', instance.name, filename)


def get_upload_path_categories(instance, filename):
    return os.path.join(settings.MEDIA_ROOT, 'images/categories/', instance.title, filename)


def get_upload_path_products(instance, filename):
    return os.path.join(settings.MEDIA_ROOT, 'images/products/', instance.code, filename)


def get_upload_path_models(instance, filename):
    return os.path.join(settings.MEDIA_ROOT, 'images/products/', instance.product.product_id.__str__(), instance.code, filename)


def get_upload_path_payments(instance, filename):
    return os.path.join(settings.MEDIA_ROOT, 'images/payments/', instance.payment_id.__str__(), filename)


# Generate Random Code for Orders
def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_order_id_generator(instance):
    try:
        order_new_code = random_string_generator()
        klass = instance.__class__

        x = klass.objects.filter(tracking_code=order_new_code)
        if not x.exists():
            return order_new_code
        else:
            return unique_order_id_generator(instance)

    except IntegrityError:
        return unique_order_id_generator(instance)


class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'خطایی در سرور رخ داده است.'

    def __init__(self, detail, field, status_code):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_text(detail)}
        else:
            self.detail = {'detail': force_text(self.default_detail)}