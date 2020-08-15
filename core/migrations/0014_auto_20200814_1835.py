# Generated by Django 3.0.8 on 2020-08-14 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20200814_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='models', to='core.Color'),
        ),
    ]
