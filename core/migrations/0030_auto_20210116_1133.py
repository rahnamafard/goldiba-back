# Generated by Django 3.0.8 on 2021-01-16 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20210116_1109'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='city',
            new_name='city_name',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='province',
            new_name='province_name',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='send_method',
            new_name='send_method_name',
        ),
    ]
