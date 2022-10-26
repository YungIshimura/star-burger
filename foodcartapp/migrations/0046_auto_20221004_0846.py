# Generated by Django 3.2.15 on 2022-10-04 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('raw', 'Необработанный'), ('prepare', 'Готовиться'), ('delivered', 'Передан курьеру'), ('completed', 'Выполнен')], db_index=True, default='raw', max_length=20, verbose_name='Статус заказа'),
        ),
    ]