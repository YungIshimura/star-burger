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

    date = models.DateTimeField(
        'Дата запроса',
        unique=True
    )

    class Meta:
        verbose_name = 'Месторасположение ресторана'
    
    def __str__(self):
        return self.address