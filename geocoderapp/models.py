from django.db import models


class GeoCode(models.Model):
    latitude = models.FloatField(
        'Широта',
        unique=True
    )

    longitude = models.FloatField(
        'Долгота',
        unique=True
    )

    address = models.CharField(
        'адрес ресторана',
        max_length=100,
        unique=True
    )

    requested_at = models.DateTimeField(
        'Дата запроса',
    )

    class Meta:
        verbose_name = 'Месторасположение ресторана'
        verbose_name_plural = 'Месторасположение ресторанов'

    def __str__(self):
        return self.address
