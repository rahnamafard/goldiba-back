# Generated by Django 3.0.8 on 2020-10-07 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='models',
            field=models.ManyToManyField(related_name='orders', through='core.OrderModel', to='core.Model'),
        ),
    ]
