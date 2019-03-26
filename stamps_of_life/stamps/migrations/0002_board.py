# Generated by Django 2.1.7 on 2019-03-23 19:03

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('stamps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('stamped_at', models.DateTimeField(auto_now_add=True)),
                ('tag', models.CharField(max_length=32)),
                ('desire', models.CharField(max_length=32)),
                ('is_active', models.BooleanField(default=True)),
                ('stamp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stamps.Stamp')),
            ],
        ),
    ]