# Generated by Django 4.0.4 on 2022-06-06 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_alter_order_order_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_identifier',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
