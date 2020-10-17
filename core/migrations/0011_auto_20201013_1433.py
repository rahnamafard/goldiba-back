# Generated by Django 3.0.8 on 2020-10-13 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20201012_1637'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transaction_id', models.AutoField(primary_key=True, serialize=False)),
                ('ref_number', models.CharField(max_length=32, verbose_name='Transaction Reference Number')),
                ('amount', models.PositiveIntegerField(verbose_name='Transaction Amount')),
                ('card_number', models.CharField(max_length=32, verbose_name='Source Cart')),
                ('description', models.TextField(max_length=255, verbose_name='Transaction Description')),
                ('paid_at', models.DateTimeField(verbose_name='Transaction Date/Time')),
                ('status', models.CharField(choices=[('PE', 'Pending'), ('OK', 'Successful'), ('ER', 'Unsuccessful')], default='PE', max_length=2)),
                ('method', models.CharField(choices=[('ZB', 'Zibal'), ('BM', 'Behpardakht Mellat'), ('OF', 'Offline.')], default='OF', max_length=2)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='core.Order')),
            ],
        ),
        migrations.CreateModel(
            name='ZibalPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(verbose_name='Zibal Payment Amount')),
                ('track_id', models.CharField(max_length=32, verbose_name='Zibal trackId')),
                ('success', models.BooleanField(default=0, verbose_name='Zibal Payment Successful?')),
                ('status', models.SmallIntegerField(verbose_name='Zibal Payment Status')),
            ],
        ),
        migrations.RemoveField(
            model_name='payment',
            name='order',
        ),
        migrations.RemoveField(
            model_name='product',
            name='auctions',
        ),
        migrations.RemoveField(
            model_name='product',
            name='gifts',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tags',
        ),
        migrations.DeleteModel(
            name='Auction',
        ),
        migrations.DeleteModel(
            name='Gift',
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
