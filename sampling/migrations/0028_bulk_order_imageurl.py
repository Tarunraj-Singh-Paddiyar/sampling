# Generated by Django 4.2.10 on 2024-04-16 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampling', '0027_remove_bulk_order_selected_samples_bulk_order_length_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulk_order',
            name='imageurl',
            field=models.CharField(default='/None/', max_length=150),
        ),
    ]
