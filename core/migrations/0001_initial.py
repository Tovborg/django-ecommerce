# Generated by Django 4.0.4 on 2022-06-08 14:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(max_length=100)),
                ('apartment_address', models.CharField(max_length=100)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('zip', models.CharField(max_length=100)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('field_name', models.CharField(default='default', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70, verbose_name='Product Name')),
                ('price', models.FloatField(verbose_name='Price')),
                ('discount_price', models.FloatField(blank=True, null=True)),
                ('label', models.CharField(choices=[
                 ('NC', 'New collection'), ('T', 'Trending'), ('OBG', 'Old but gold')], max_length=4)),
                ('home_page_image', models.ImageField(
                    blank=True, null=True, upload_to='uploads/')),
                ('shop_grid_image', models.ImageField(
                    blank=True, null=True, upload_to='uploads/')),
                ('slug', models.SlugField()),
                ('description', models.TextField(
                    max_length=190, verbose_name='Description')),
                ('featured', models.BooleanField(default=False)),
                ('times_ordered', models.IntegerField(default=1)),
                ('featured_products', models.CharField(blank=True, choices=[('NA', 'New arrival'), (
                    'BS', 'Best selling'), ('OS', 'On sale'), ('FY', 'For you')], max_length=10, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('category', models.ManyToManyField(to='core.category')),
                ('color', models.ManyToManyField(to='core.color')),
            ],
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='to_contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('items', models.ManyToManyField(blank=True, to='core.item')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewer', models.CharField(max_length=100, null=True)),
                ('stars', models.IntegerField(default=1)),
                ('review_text', models.TextField(
                    max_length=800, verbose_name='review content')),
                ('review_date', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='core.item')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('quantity', models.IntegerField(default=1)),
                ('item', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='core.item')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                                           primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=150)),
                ('amount', models.IntegerField(default=0)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('ordered_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('ordered', models.BooleanField(default=False)),
                ('order_identifier', models.IntegerField(
                    blank=True, default=0, null=True)),
                ('billing_address', models.ForeignKey(blank=True, null=True,
                                                      on_delete=django.db.models.deletion.SET_NULL, to='core.billingaddress')),
                ('items', models.ManyToManyField(to='core.orderitem')),
                ('user', models.ForeignKey(blank=True, null=True,
                                           on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='sizes',
            field=models.ManyToManyField(blank=True, to='core.size'),
        ),
    ]
