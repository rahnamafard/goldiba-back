# Generated by Django 3.0.8 on 2020-10-09 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20201009_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendmethod',
            name='alternative_price_text',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Text Alternative For Price'),
        ),
    ]