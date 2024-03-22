# Generated by Django 4.2.10 on 2024-03-09 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampling', '0012_ordercounter_remove_order_id_order_orderno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='selected_samples',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='ordercounter',
            name='current_number',
            field=models.IntegerField(default=1000),
        ),
    ]
