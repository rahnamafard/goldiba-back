# Generated by Django 3.0.8 on 2020-10-07 18:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_order_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermodel',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Order'),
        ),
    ]
