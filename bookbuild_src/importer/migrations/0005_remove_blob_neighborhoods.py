# Generated by Django 4.1.7 on 2023-03-05 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("importer", "0004_blob_neighborhoods_blob_soft_delete"),
    ]

    operations = [
        migrations.RemoveField(model_name="blob", name="neighborhoods",),
    ]