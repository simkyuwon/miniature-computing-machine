# Generated by Django 3.1 on 2021-05-24 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notepadDB', '0004_file_editing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='editing',
        ),
    ]
