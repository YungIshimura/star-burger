from datetime import datetime

import requests
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem
from geocoderapp.models import GeoCode
from star_burger.settings import YANDEX_API_KEY


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(
            restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"

    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })

    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

    return lon, lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.full_price().select_related('customer')
    processed_orders = []

    for order in orders:
        restaurants = RestaurantMenuItem.objects.filter(
            product=order.product
        ).prefetch_related('product').select_related('restaurant')

        customer_orders = orders.filter(
            customer=order.customer.id).select_related('customer')

        for customer_order in customer_orders:
            order_items = {
                'id': customer_order.id,
                'status': order.get_status_display(),
                'payment': order.customer.get_payment_display(),
                'price': sum([order.full_price for order in customer_orders]),
                'customer': customer_order.customer,
                'phonenumber': customer_order.customer.phonenumber,
                'address': customer_order.customer.address,
                'comment': customer_order.customer.comment,
            }

            if customer_order.customer.restaurant:
                order_items.update(
                    {
                        'will_cook': customer_order.customer.restaurant
                    }
                )

                order.status = 'prepare'
                order.save()

            restaurants_geocode = []

        user_lon, user_lat = fetch_coordinates(
            YANDEX_API_KEY, order.customer.address
        )

        for restaurant in restaurants:
            if order.product.name == restaurant.product.name:
                try:
                    geocoder = GeoCode.objects.get(
                        address=restaurant.restaurant.address)
                    rest_lat, rest_lon = geocoder.latitude, geocoder.longitude

                    distanse = int(distance.distance(
                        (user_lat, user_lon), (rest_lat, rest_lon)).km)

                    restaurant = {
                        restaurant.restaurant.name: distanse}
                    restaurants_geocode.append(restaurant)

                except:

                    rest_lon, rest_lat = fetch_coordinates(
                        YANDEX_API_KEY, restaurant.restaurant.address
                    )
                    GeoCode.objects.create(
                        latitude=rest_lat,
                        longitude=rest_lon,
                        address=restaurant.restaurant.address,
                        date=datetime.now()
                    )
                    distanse = int(distance.distance(
                        (user_lat, user_lon), (rest_lat, rest_lon)).km)

                    restaurant = {
                        restaurant.restaurant.name: distanse}
                    restaurants_geocode.append(restaurant)

        order_items.update({
            'restaurants': restaurants_geocode
        })

        if order.id == order_items['id']:
            processed_orders.append(order_items)

    return render(request, template_name='order_items.html', context={
        'order_items': processed_orders
    })
