# Generated by Django 4.0.4 on 2022-06-06 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_item_shop_grid_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='color',
            field=models.ManyToManyField(to='core.color'),
        ),
    ]
