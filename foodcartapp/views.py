from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import re

from .models import Order, Product, Сustomer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order = request.data

    if 'firstname' and 'lastname' and 'phonenumber' and 'address' not in order.keys():
        content = {
            'products, firstname, lastname, phonenumber, address: Обязательные поля, они не могут быть пустыми'}

        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    elif len(order['products']) == 0:
        content = {'products: Этот список не может быть пустым'}

        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    elif not re.match('^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', order['phonenumber']):
        content = {"phonenumber: Введен некорректный номер телефона"}

        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    elif type(order['products']) is not list:
        content = {
            f'products: Ожидался list со значениями, но был получен {type(order["products"])}'
        }

        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    elif Product.objects.last().id < order['products'][0]['product']:
        content = {
            f'products: Недопустимый первичный ключ {order["products"][0]["product"]}'}

        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    elif order['firstname'] is not str:
        content = {'firstname: это не строка'}

        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    else:
        customer = Сustomer.objects.create(
            name=order['firstname'],
            surname=order['lastname'],
            phone_number=order['phonenumber'],
            address=order['address'],
        )
        for products in order['products']:
            product = Product.objects.get(id=products['product'])
            Order.objects.create(
                customer=customer,
                product=product,
                quantity=products['quantity']
            )

    return Response()
