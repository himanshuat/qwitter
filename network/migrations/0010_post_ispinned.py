# Generated by Django 4.2.3 on 2024-09-06 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0009_auto_20230713_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='ispinned',
            field=models.BooleanField(default=False),
        ),
    ]
