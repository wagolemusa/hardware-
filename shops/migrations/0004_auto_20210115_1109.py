# Generated by Django 2.2.15 on 2021-01-15 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0003_auto_20210114_1616'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='categories',
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ManyToManyField(related_name='category_set', to='shops.Category'),
        ),
    ]
