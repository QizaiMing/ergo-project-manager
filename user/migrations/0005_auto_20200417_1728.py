# Generated by Django 2.2.12 on 2020-04-17 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20200417_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpicture',
            name='picture',
            field=models.ImageField(upload_to='media'),
        ),
    ]
