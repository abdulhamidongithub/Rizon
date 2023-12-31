# Generated by Django 5.0 on 2023-12-27 06:57

import django.core.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LandingProductOrder',
            fields=[
                ('date', models.DateTimeField(auto_created=True, auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('customer', models.CharField(max_length=255)),
                ('amount', models.SmallIntegerField()),
                ('done', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('date', models.DateTimeField(auto_created=True, auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('price', models.BigIntegerField()),
                ('extraPrice', models.BigIntegerField(null=True)),
                ('about', models.TextField(null=True)),
                ('photo_link', models.FileField(blank=True, null=True, upload_to='product_photos')),
                ('discount', models.SmallIntegerField(null=True)),
                ('deleted', models.BooleanField(default=False, null=True)),
                ('manufacturer', models.CharField(default='Alkimyogar Pharm', max_length=255)),
                ('expiration_date', models.CharField(default='1 yil', max_length=255)),
                ('product_type', models.CharField(default='sirop', max_length=255)),
                ('rate', models.BigIntegerField(default=5, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductComment',
            fields=[
                ('dateTime', models.DateTimeField(auto_created=True, auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(max_length=255)),
                ('job', models.CharField(max_length=255, null=True)),
                ('photo', models.FileField(blank=True, null=True, upload_to='clients')),
                ('comment', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductDiscount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('amount', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('discount', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('startDate', models.DateTimeField()),
                ('endDate', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductOrder',
            fields=[
                ('date', models.DateTimeField(auto_created=True, auto_now_add=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('amount', models.SmallIntegerField()),
                ('done', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
