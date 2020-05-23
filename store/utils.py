import json
from .models import *


def cookie_cart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart:', cart)
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cart_items = order['get_cart_items']

    for i in cart:
        try:
            cart_items += cart[i]['quantity']
            product = Product.objects.get(pk=i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image_url': product.image.url,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'cart_items': cart_items, 'order': order, 'items': items}


def cart_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items

    else:
        cookie_data = cookie_cart(request)
        cart_items = cookie_data['cart_items']
        order = cookie_data['order']
        items = cookie_data['items']
    return{'cart_items': cart_items, 'order': order, 'items': items}


def guest_order(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookie_data = cookie_cart(request)
    items = cookie_data['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(pk=item['product']['id'])

        order_item = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )

    return customer, order
