# Generated by Django 3.2.15 on 2022-10-13 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_auto_20221006_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.CharField(blank=True, max_length=200, verbose_name='Адрес доставки'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='firstname',
            field=models.CharField(blank=True, max_length=20, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='lastname',
            field=models.CharField(blank=True, max_length=50, verbose_name='Фамилия'),
        ),
    ]
