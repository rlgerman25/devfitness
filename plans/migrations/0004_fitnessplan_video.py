# Generated by Django 3.1.7 on 2021-03-28 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0003_auto_20210328_2111'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitnessplan',
            name='video',
            field=models.TextField(blank=True, max_length=250),
        ),
    ]
