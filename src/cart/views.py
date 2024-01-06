from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import etag
from django.views.generic import TemplateView
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
import json

from products.models import Product
from orders.models import *
from billing.models import Customer
from addresses.forms import AddressForm
  
@etag(None)
def updateItem(request):
    productId = request.GET.get('productId')
    action = request.GET.get('action')
    quantity = request.GET.get('quantity', 1)
    
    print('Action: ', action)
    print('Product: ', productId)
    print('Quantity: ', quantity)
    
    customer = request.user.customer
    product = get_object_or_404(Product, id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    
    if action == 'add':
        orderItem.quantity += int(quantity)
    elif action == 'minus':
        orderItem.quantity -= int(quantity)
    elif action == 'remove':
        orderItem.quantity = 0
        
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()

    total_quantity = OrderItem.objects.filter(order__customer=customer, order__complete=False).aggregate(Sum('quantity'))['quantity__sum']
    
    
    cart_items_count = total_quantity if total_quantity is not None else 0
    
    product_data = {
        'id': product.id,
        'name': product.name,
        'price': str(product.price),
        'quantity': orderItem.quantity,
        'total': str(orderItem.get_total),
    }
    
    return JsonResponse({
        'cart_items': cart_items_count,
        'products': [{
            'id': product.id,
            'name': product.name,
            'image': getattr(product.images.first(), 'image', None).url if product.images.first() else None,
            'quantity': orderItem.quantity,
            'total': orderItem.get_total,
        }],
        'action': action
    }, safe=False)


def checkout(request):
    shipping_form = AddressForm()

    if request.method == 'POST':
        order = Order.objects.get_or_create(customer=request.user.customer, complete=False)[0]

        shipping_form = AddressForm(request.POST)
        if shipping_form.is_valid():
            customer = get_object_or_404(Customer, user=request.user)
            
            shipping_address = shipping_form.save(commit=False)
            shipping_address.customer = customer
            shipping_address.save()
            order.shipping_address = shipping_address
            order.contact_number = shipping_address.phone

        order.save()

        return redirect('cart:checkout')

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        ordered_items = []
        with transaction.atomic():
            existing_order_items = order.orderitem_set.all()
            for order_item in existing_order_items:
                product = order_item.product
                ordered_items.append(OrderItem(order=order, product=product, quantity=order_item.quantity))   
            order.save()
    
    else:
        
        order = {
            'get_cart_total': 0, 
            'get_cart_items': 0, 
            'shipping': False
            }

    context = {
        'order': order,
        'shipping_form': shipping_form,
    }
    return render(request, "cart/shop-checkout-2.html", context)


def checkout_done_view(request):
    
    if request.user.is_authenticated:
        customer = request.user.customer
        print(f"Customer: {customer}")

        order = Order.objects.filter(customer=customer, complete=False).first()
        
        if order:
            with transaction.atomic():
                existing_order_items = order.orderitem_set.all()
                for order_item in existing_order_items:
                    product = order_item.product
                    product.stock -= order_item.quantity
                    product.save()  
                ordered_items = list(existing_order_items)
                order.complete = True
                existing_order_items.delete()
                OrderItem.objects.bulk_create(ordered_items)
                
            order.save()
            
            # Fetch the ordered items associated with the completed order
            ordered_items = OrderItem.objects.filter(order=order)
            total_quantity = sum(item.quantity for item in ordered_items)
            total_amount = sum(item.get_total for item in ordered_items)

            print("Ordered Items:", ordered_items)
            order_data = {
                'order_id': order.order_id,
                'customer': order.customer,
                'shipping_address': order.shipping_address,
                'complete': True,
                'created_at': timezone.now(),
                'ordered_items': ordered_items,
                'total_quantity': total_quantity,
                'total_amount': total_amount,
            }

            context = {
                        'order': order_data, 
                        'customer': customer,
                        }
            return render(request, "cart/shop-checkout-complete.html", context)
        else:
            completed_order = Order.objects.filter(customer=customer, complete=True).order_by('-created_at').first()
            print(f"Completed Order ID: {completed_order.order_id}")

            if completed_order:
                ordered_items = OrderItem.objects.filter(order=completed_order)

                print("Ordered Items:", ordered_items)
                total_quantity = sum(item.quantity for item in ordered_items)
                total_amount = sum(item.get_total for item in ordered_items)
                order_data = {
                    'order_id': completed_order.order_id,
                    'customer': completed_order.customer,
                    'shipping_address': completed_order.shipping_address,
                    'complete': True,
                    'created_at': timezone.now(),
                    'ordered_items': ordered_items,
                    'total_quantity': total_quantity,
                    'total_amount': total_amount,
                }

                context = {
                            'order': order_data, 
                            'customer': customer,
                           }
                return render(request, "cart/shop-checkout-complete.html", context)
            else:
                return render(request, "cart/shop-cart.html")
    else:
        return redirect('login:login')




