# Generated by Django 3.0.8 on 2020-08-17 11:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20200814_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='code',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Model Code'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('parameter_type', models.CharField(choices=[('BP', 'Before Payment'), ('AP', 'After Payment')], default='BP', max_length=2)),
                ('tracking_code', models.CharField(max_length=10, unique=True, verbose_name='Tracking Code')),
                ('phone', models.CharField(max_length=15, verbose_name='Reciever Phone Name')),
                ('postal_code', models.CharField(max_length=15, verbose_name='Receiver Postal Code')),
                ('postal_address', models.CharField(max_length=255, verbose_name='Reciever Postal Address')),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('total_price', models.PositiveIntegerField(verbose_name='Total Price')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
