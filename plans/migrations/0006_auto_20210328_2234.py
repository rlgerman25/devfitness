# Generated by Django 3.1.7 on 2021-03-28 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0005_auto_20210328_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitnessplan',
            name='image_credit',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='fitnessplan',
            name='video_credit',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
