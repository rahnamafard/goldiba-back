# Generated by Django 3.0.8 on 2020-09-07 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20200907_1530'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametercategory',
            name='compare',
        ),
        migrations.AddField(
            model_name='parameter',
            name='compare',
            field=models.BooleanField(default=False, verbose_name='Comparable'),
        ),
    ]
