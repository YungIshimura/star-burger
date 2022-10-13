from rest_framework.serializers import ModelSerializer
from .models import Order, Customer


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['product', 'quantity']


class CustomerSerializer(ModelSerializer):
    products = OrderSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'firstname', 'lastname',
                  'phonenumber', 'address', 'products']
