# Generated by Django 4.1.7 on 2023-03-10 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("importer", "0011_blob_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="order",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="neighborhood",
            name="order",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="section",
            name="order",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
