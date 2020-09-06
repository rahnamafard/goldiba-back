from django.db import IntegrityError
import random
import string
import os

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


# Generate Random Code for Orders
def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_order_id_generator(instance):
    order_new_code = random_string_generator()
    klass = instance.__class__

    try:
        x = klass.objects.filter(tracking_code=order_new_code)
        if not x.exists():
            return order_new_code
        else:
            return unique_order_id_generator(instance)

    except IntegrityError:
        return unique_order_id_generator(instance)
