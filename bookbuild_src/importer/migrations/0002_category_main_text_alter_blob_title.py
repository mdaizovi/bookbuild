# Generated by Django 4.1.7 on 2023-02-24 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("importer", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="main_text",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="blob", name="title", field=models.CharField(max_length=200),
        ),
    ]
