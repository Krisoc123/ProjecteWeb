# Generated by Django 5.1.6 on 2025-05-17 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_alter_exchange_book2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='points',
            field=models.IntegerField(default=50),
        ),
    ]
