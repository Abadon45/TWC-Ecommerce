# Generated by Django 5.1.1 on 2024-09-23 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinestore', '0002_address_rating_review'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255)),
                ('number_1', models.IntegerField()),
                ('number_2', models.IntegerField()),
                ('total', models.IntegerField()),
            ],
        ),
    ]
