# Generated by Django 4.0.4 on 2022-06-16 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_order_shipping_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingaddress',
            name='zip',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]