# Generated by Django 3.2.15 on 2022-11-02 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0059_rename_order_orderitem'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Customer',
            new_name='Order',
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'verbose_name': 'Атрибуты заказа', 'verbose_name_plural': 'Атрибуты заказов'},
        ),
    ]
