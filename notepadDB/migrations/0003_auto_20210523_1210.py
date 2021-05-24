# Generated by Django 3.1 on 2021-05-23 12:10

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('notepadDB', '0002_auto_20210523_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='folder',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
