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
from django.db.models import OuterRef
from foodcartapp.models import Order, OrderItem, Product, Restaurant, RestaurantMenuItem
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


def get_restaurants_geocode(order_item, restaurants):
    restaurants_geocode = []
    user_lon, user_lat = fetch_coordinates(
        YANDEX_API_KEY, order_item.order.address
    )

    for restaurant in restaurants:
        if order_item.product.name == restaurant.product.name:
            try:
                geocoder = GeoCode.objects.get(
                    address=restaurant.restaurant.address)
                rest_lat, rest_lon = geocoder.latitude, geocoder.longitude

                distance_to_restaurant = int(distance.distance(
                    (user_lat, user_lon), (rest_lat, rest_lon)).km)

                restaurant_geocode = {
                    restaurant.restaurant.name: distance_to_restaurant}

                restaurants_geocode.append(restaurant_geocode)

            except GeoCode.DoesNotExist as e:
                rest_lon, rest_lat = fetch_coordinates(
                    YANDEX_API_KEY, restaurant.address
                )
                GeoCode.objects.create(
                    latitude=rest_lat,
                    longitude=rest_lon,
                    address=restaurant.address,
                    requested_at=datetime.now()
                )
                distance_to_restaurant = int(distance.distance(
                    (user_lat, user_lon), (rest_lat, rest_lon)).km)

                restaurant_geocode = {
                    restaurant.restaurant.name: distance_to_restaurant}

                restaurants_geocode.append(restaurant_geocode)

    return restaurants_geocode


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.all().get_amount()
    order_items = OrderItem.objects.all().select_related('product', 'order')
    order_items_for_subquery = OrderItem.objects.filter(
        product=OuterRef('product'))

    restaurants = RestaurantMenuItem.objects.get_restaurants_can_cook(
        order_items_for_subquery).prefetch_related('product').select_related('restaurant')

    processed_orders = []

    for order in orders:
        order_attr_for_managers = {
            'id': order.id,
            'status': order.get_status_display(),
            'payment_method': order.get_payment_method_display(),
            'price': orders.get(id=order.id).amount,
            'order': order,
            'phonenumber': order.phonenumber,
            'address': order.address,
            'comment': order.comment,
        }

        if order.provider:
            order_attr_for_managers.update(
                {
                    'will_cook': order.provider
                })

            order.status = 'prepare'
            order.save()

        for order_item in order_items:
            restaurants_geocode = get_restaurants_geocode(
                order_item, restaurants
            )

            order_attr_for_managers.update({
                'restaurants': restaurants_geocode
            })

        processed_orders.append(order_attr_for_managers)

    return render(request, template_name='order_items.html', context={
        'order_items': processed_orders
    })
