# Generated by Django 3.0.8 on 2020-10-12 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20201009_1904'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='product',
            new_name='order',
        ),
    ]
