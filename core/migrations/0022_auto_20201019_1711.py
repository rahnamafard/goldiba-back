# Generated by Django 3.0.8 on 2020-10-19 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20201019_1711'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordermodel',
            old_name='id',
            new_name='order_model_id',
        ),
        migrations.RenameField(
            model_name='zibalpayment',
            old_name='id',
            new_name='zibal_payment_id',
        ),
    ]