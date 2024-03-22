# Generated by Django 4.2.10 on 2024-03-09 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampling', '0013_alter_order_selected_samples_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='completestatus',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='selected_samples',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
