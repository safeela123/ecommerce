# Generated by Django 5.2 on 2025-06-26 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0011_order_refund_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add2',
            name='stock',
            field=models.IntegerField(default='in stock'),
        ),
    ]
