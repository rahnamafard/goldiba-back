# Generated by Django 3.0.8 on 2021-01-24 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_product_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='recharged_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]