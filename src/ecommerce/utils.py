import datetime 
import os
import random
import string
import uuid

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime
import string

User = get_user_model()


def random_string_generator(size=10, chars=string.ascii_uppercase + string.digits):
    current_time_ms = int(datetime.now().timestamp() * 1000)
    date_string = f"{current_time_ms:0>10}"
    random_letters = "".join(random.choice(chars) for _ in range(size - len(date_string)))
    combined_string = f"TWC{date_string}{random_letters.upper()}"
    return combined_string

def unique_order_id_generator(instance, size=6, chars=string.ascii_uppercase + string.digits):
    if instance:
        order_new_id = random_string_generator(size=size, chars=chars)
        Klass = instance.__class__

        while Klass.objects.filter(order_id=order_new_id).exists():
            order_new_id = random_string_generator(size=size, chars=chars)

        return order_new_id
    else:
        return random_string_generator(size=size, chars=chars)

def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with an 'order_id' field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.order_id)  # Use the correct field for your model

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=random_string_generator(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def is_valid_username(username):
    try:
        User.objects.get(username=username)
        return True
    except User.DoesNotExist:
        return False