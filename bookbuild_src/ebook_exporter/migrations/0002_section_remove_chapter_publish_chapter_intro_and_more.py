# Generated by Django 4.1.7 on 2023-10-08 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ebook_exporter", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Section",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("order", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("main_text", models.TextField(blank=True, null=True)),
            ],
            options={"ordering": ["chapter", "order"],},
        ),
        migrations.RemoveField(model_name="chapter", name="publish",),
        migrations.AddField(
            model_name="chapter",
            name="intro",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="book",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="ebook_exporter.book",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="chapter",
            name="src",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.CreateModel(
            name="Subsection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=200)),
                ("order", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("priority", models.PositiveSmallIntegerField(blank=True, null=True)),
                (
                    "category_text",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("main_text", models.TextField(blank=True, null=True)),
                ("footer_text", models.TextField(blank=True, null=True)),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="ebook_exporter.section",
                    ),
                ),
            ],
            options={"ordering": ["section", "priority", "order"],},
        ),
        migrations.AddField(
            model_name="section",
            name="chapter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="ebook_exporter.chapter"
            ),
        ),
    ]
