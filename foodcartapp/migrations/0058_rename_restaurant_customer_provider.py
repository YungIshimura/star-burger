# Generated by Django 3.2.15 on 2022-10-31 21:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0057_alter_order_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='restaurant',
            new_name='provider',
        ),
    ]