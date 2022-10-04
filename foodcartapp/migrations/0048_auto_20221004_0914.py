# Generated by Django 3.2.15 on 2022-10-04 09:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20221004_0910'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='called_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время и дата звонка'),
        ),
        migrations.AddField(
            model_name='customer',
            name='delivered_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время и дата доставки'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='registered_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время и дата заказа'),
        ),
    ]
