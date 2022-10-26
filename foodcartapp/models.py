from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=300,
        blank=True,
    )
    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Customer(models.Model):
    PAYMENT_METHOD = (
        ('not specified', 'Не указан'),
        ('cash', 'Наличными'),
        ('card', 'Картой')
    )
    firstname = models.CharField(
        'Имя',
        max_length=20,
        blank=True
    )

    lastname = models.CharField(
        'Фамилия',
        max_length=50,
        blank=True
    )

    address = models.CharField(
        'Адрес доставки',
        max_length=200,
        blank=True
    )

    phonenumber = PhoneNumberField(
        'Номер телефона',
    )

    comment = models.TextField(
        'Комментарий',
        blank=True,
        null=True
    )
    registered_at = models.DateTimeField(
        'Время и дата заказа',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Время и дата звонка',
        blank=True,
        null=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'Время и дата доставки',
        blank=True,
        null=True,
        db_index=True
    )
    payment = models.CharField(
        'Способ оплаты',
        max_length=15,
        choices=PAYMENT_METHOD,
        default='not specified',
        db_index=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='restaurant',
        verbose_name='Кто приготовит'
    )

    class Meta:
        verbose_name = 'Заказчик'
        verbose_name_plural = 'Заказчики'

    def __str__(self):
        return f'{self.id} {self.firstname} {self.lastname}'


class OrderQuerySet(models.QuerySet):
    def full_price(self):
        full_price = self.annotate(full_price=Sum(
            F('quantity') * F('product__price')))

        return full_price


class Order(models.Model):
    STATUS = (
        ('raw', 'Необработанный'),
        ('prepare', 'Готовиться'),
        ('delivered', 'Передан курьеру'),
        ('completed', 'Выполнен')
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='order',
        verbose_name='Заказчик')

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        default=None,
        related_name='product',
        verbose_name='продукт',
    )
    final_price = models.DecimalField(
        'Окончательная стоимость',
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.IntegerField(
        'Количество',
        default=1,
        validators=[MinValueValidator(1)])

    status = models.CharField(
        'Статус заказа',
        max_length=20,
        choices=STATUS,
        default='raw',
        db_index=True
    )
    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f'{self.id} {self.customer} - {self.product}: {self.quantity}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
