# Generated by Django 3.1.1 on 2020-09-01 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userMessages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='subject',
            field=models.CharField(max_length=35),
        ),
    ]