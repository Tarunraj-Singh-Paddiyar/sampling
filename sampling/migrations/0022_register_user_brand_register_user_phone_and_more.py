# Generated by Django 4.2.10 on 2024-03-22 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sampling', '0021_alter_designs_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='register_user',
            name='brand',
            field=models.CharField(default='default', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='register_user',
            name='phone',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='register_user',
            name='email',
            field=models.CharField(max_length=100),
        ),
    ]
