# Generated by Django 4.0.4 on 2022-06-04 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_wishlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='items',
            field=models.ManyToManyField(blank=True, to='core.item'),
        ),
    ]
