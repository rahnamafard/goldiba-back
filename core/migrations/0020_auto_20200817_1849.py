# Generated by Django 3.0.8 on 2020-08-17 14:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20200817_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='tracking_code',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=10, unique=True, verbose_name='Tracking Code'),
        ),
    ]
