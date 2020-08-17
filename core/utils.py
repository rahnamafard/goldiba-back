import random
import string

from django.db import IntegrityError

from core.models import Order


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_order_id_generator(instance):
    order_new_code = random_string_generator()

    # Klass = instance.__class__

    # qs_exists = Klass.objects.filter(tracking_code=order_new_code).exists()

    try:
        x = Order.objects.filter(tracking_code=order_new_code)
        if not x.exists():
            return order_new_code
        else:
            return unique_order_id_generator(instance)

    except IntegrityError:
        return unique_order_id_generator(instance)

