# Generated by Django 4.2.10 on 2024-03-22 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampling', '0022_register_user_brand_register_user_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='register_user',
            name='phone',
            field=models.CharField(max_length=30),
        ),
    ]
