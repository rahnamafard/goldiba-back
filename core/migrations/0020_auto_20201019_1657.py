# Generated by Django 3.0.8 on 2020-10-19 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_image'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.RemoveField(
            model_name='offlinepayment',
            name='id',
        ),
        migrations.AddField(
            model_name='offlinepayment',
            name='offline_payment_id',
            field=models.AutoField(default=None, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
