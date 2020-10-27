# Generated by Django 3.0.8 on 2020-10-27 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20201025_1618'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='expired',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('PE', 'Pending'), ('AP', 'Approved'), ('EX', 'Expired')], default='PE', max_length=2),
        ),
    ]
