# Generated by Django 2.1.7 on 2019-03-25 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stamps', '0003_auto_20190323_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='stamp',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
