# Generated by Django 3.2.15 on 2022-10-04 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_auto_20221001_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('raw', 'Необработанный'), ('prepare', 'Готовиться'), ('delivered', 'Передан курьеру'), ('completed', 'Выполнен')], default='raw', max_length=20),
        ),
    ]