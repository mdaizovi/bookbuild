# Generated by Django 4.1.7 on 2023-03-05 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("importer", "0006_blob_categories"),
    ]

    operations = [
        migrations.RemoveField(model_name="blob", name="category",),
    ]
