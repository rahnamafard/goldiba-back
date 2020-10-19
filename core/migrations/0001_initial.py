# Generated by Django 3.0.8 on 2020-10-07 17:10

import core.models
import core.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Last Name')),
                ('username', models.CharField(blank=True, max_length=64, null=True, verbose_name='Username')),
                ('password', models.CharField(blank=True, max_length=255, null=True, verbose_name='Password')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email Address')),
                ('mobile', models.CharField(max_length=15, unique=True, verbose_name='Mobile Phone Number')),
                ('email_subscription', models.BooleanField(blank=True, null=True, verbose_name='Email Newsletter')),
                ('sms_subscription', models.BooleanField(blank=True, null=True, verbose_name='SMS Newsletter')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', core.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('auction_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Auction Title')),
                ('percent', models.PositiveIntegerField(verbose_name='Off Percentage')),
                ('start_date', models.DateTimeField(verbose_name='Start Time/Date')),
                ('end_date', models.DateTimeField(verbose_name='Start Time/Date')),
                ('cover', models.ImageField(blank=True, null=True, upload_to='images/auction/<django.db.models.fields.AutoField>/')),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('brand_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='Persian Name')),
                ('english_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='English Name')),
                ('image', models.ImageField(blank=True, null=True, upload_to=core.utils.get_upload_path_brands)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='Category Title')),
                ('cover', models.ImageField(blank=True, max_length=255, null=True, upload_to=core.utils.get_upload_path_categories)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.Category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('color_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='Color Name')),
                ('hex', models.CharField(max_length=32, verbose_name='HEX Code')),
            ],
        ),
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('gift_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='Gift Title')),
                ('cover', models.ImageField(blank=True, null=True, upload_to='images/gift/<django.db.models.fields.AutoField>/')),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('model_id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=32, verbose_name='Model Code')),
                ('title', models.CharField(max_length=255, verbose_name='Model Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('price', models.PositiveIntegerField(verbose_name='Price')),
                ('in_stock', models.PositiveSmallIntegerField(verbose_name='# In Stock')),
                ('image', models.ImageField(upload_to=core.utils.get_upload_path_models)),
                ('is_active', models.BooleanField(blank=True, default=1, null=True, verbose_name='Activation Status')),
                ('color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='models', to='core.Color')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('parameter_type', models.CharField(choices=[('PE', 'Pending'), ('AP', 'Approved'), ('RJ', 'Rejected')], default='PE', max_length=2)),
                ('tracking_code', models.CharField(max_length=10, verbose_name='Tracking Code')),
                ('phone', models.CharField(max_length=15, verbose_name='Receiver Phone Name')),
                ('postal_code', models.CharField(max_length=15, verbose_name='Receiver Postal Code')),
                ('postal_address', models.TextField(max_length=255, verbose_name='Receiver Postal Address')),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('total_price', models.PositiveIntegerField(verbose_name='Total Price')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ParameterCategory',
            fields=[
                ('parameter_category_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='Parameter Category Title')),
            ],
            options={
                'verbose_name_plural': 'Parameter categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True)),
                ('code', models.CharField(error_messages={'unique': 'محصولی با این کد وجود دارد.'}, max_length=32, unique=True, verbose_name='Product Code')),
                ('discount', models.PositiveSmallIntegerField(default=0, verbose_name='Product Discount')),
                ('free_send', models.BooleanField(verbose_name='Free Send')),
                ('main_image', models.ImageField(upload_to=core.utils.get_upload_path_products)),
                ('second_image', models.ImageField(blank=True, null=True, upload_to=core.utils.get_upload_path_products)),
                ('size_image', models.ImageField(blank=True, null=True, upload_to=core.utils.get_upload_path_products)),
                ('likes', models.PositiveIntegerField(default=0, verbose_name='Product Like Count')),
                ('auctions', models.ManyToManyField(blank=True, related_name='products', to='core.Auction')),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='core.Brand')),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('status_id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(default='', max_length=255, verbose_name='Status Title')),
            ],
            options={
                'verbose_name_plural': 'Statuses',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('tag_id', models.AutoField(primary_key=True, serialize=False)),
                ('tag', models.CharField(max_length=255, verbose_name='Tag Text')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_main_category', models.BooleanField(blank=True, default=False, null=True, verbose_name='Main Category')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Category')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Product')),
            ],
            options={
                'verbose_name_plural': 'Product categories',
                'db_table': 'core_product_cateogory',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(related_name='products', through='core.ProductCategory', to='core.Category'),
        ),
        migrations.AddField(
            model_name='product',
            name='gifts',
            field=models.ManyToManyField(blank=True, related_name='products', to='core.Gift'),
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='core.Status'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='products', to='core.Tag'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('payment_status', models.CharField(choices=[('OK', 'Successful.'), ('ER', 'Unsuccessful.')], default='ER', max_length=2)),
                ('payment_method', models.CharField(choices=[('ON', 'Online.'), ('OF', 'Offline.')], default='OF', max_length=2)),
                ('tracking_code', models.CharField(max_length=10, verbose_name='Bank Tracking Code')),
                ('attachment', models.ImageField(upload_to=core.utils.get_upload_path_offline_payments)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='core.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('parameter_id', models.AutoField(primary_key=True, serialize=False)),
                ('parameter_type', models.CharField(choices=[('ST', 'Short Text'), ('LT', 'Long Text'), ('MO', 'Multiple Options'), ('SO', 'Single Option')], default='ST', max_length=3)),
                ('name', models.CharField(max_length=255, verbose_name='Parameter Name')),
                ('compare', models.BooleanField(default=False, verbose_name='Comparable')),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Category')),
                ('parameter_category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ParameterCategory')),
            ],
        ),
        migrations.CreateModel(
            name='OrderModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(verbose_name='Price')),
                ('quantity', models.PositiveIntegerField(verbose_name='Quantity')),
                ('discount', models.PositiveSmallIntegerField(default=0, verbose_name='Product Discount')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Model')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Order')),
            ],
            options={
                'verbose_name_plural': 'Model Order',
                'db_table': 'core_order_models',
            },
        ),
        migrations.AddField(
            model_name='model',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='core.Product'),
        ),
    ]
