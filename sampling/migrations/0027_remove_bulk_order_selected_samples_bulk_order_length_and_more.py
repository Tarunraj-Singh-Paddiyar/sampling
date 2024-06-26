# Generated by Django 4.2.10 on 2024-04-13 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampling', '0026_bulk_order_remove_order_address_remove_order_brand_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bulk_order',
            name='selected_samples',
        ),
        migrations.AddField(
            model_name='bulk_order',
            name='length',
            field=models.CharField(default='None', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bulk_order',
            name='selected_design',
            field=models.CharField(default='None', max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bulk_order',
            name='width',
            field=models.CharField(default='None', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bulk_order',
            name='username',
            field=models.CharField(default='None', max_length=250),
            preserve_default=False,
        ),
    ]
