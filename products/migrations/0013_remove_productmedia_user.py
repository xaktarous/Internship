# Generated by Django 5.1.6 on 2025-02-24 14:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_productmedia_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productmedia',
            name='user',
        ),
    ]
