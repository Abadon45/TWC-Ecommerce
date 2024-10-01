from __future__ import absolute_import, unicode_literals
import random
from celery import shared_task
from .models import *

@shared_task(name="sum_two_numbers")
def script2(x, y):
    number_1 = x
    number_2 = y
    total = number_1 + number_2
    new_obj = Test.objects.create(
        item_name='items',
        number_1=number_1,
        number_2=number_2,
        total=total)
    return total

@shared_task(name="multiply_two_numbers")
def mul(x, y):
    total = x * (y * random.randint(3, 100))
    return total


@shared_task(name="sum_list_numbers")
def xsum(numbers):
    return sum(numbers)

@shared_task(name="run_test_script")
def script1(x, y):
    number_1 = x
    number_2 = (y * random.randint(3, 100))
    total =number_1 * number_2
    new_obj = Test.objects.create(
        item_name='items',
        number_1=number_1,
        number_2=number_2,
        total=total)
    return total

@shared_task(name="twc_script")
def script(x, y):
    return x + y