# Generated by Django 4.0.4 on 2022-06-03 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_reviews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviews',
            name='stars',
            field=models.IntegerField(default=1, max_length=5),
        ),
    ]