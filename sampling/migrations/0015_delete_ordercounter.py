# Generated by Django 4.2.10 on 2024-03-09 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sampling', '0014_order_completestatus_alter_order_selected_samples'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OrderCounter',
        ),
    ]
