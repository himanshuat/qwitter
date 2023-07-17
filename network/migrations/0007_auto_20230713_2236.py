# Generated by Django 3.1.6 on 2023-07-13 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_bookmark'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='bookmark',
            constraint=models.UniqueConstraint(fields=('post', 'user'), name='unique bookmark'),
        ),
    ]
