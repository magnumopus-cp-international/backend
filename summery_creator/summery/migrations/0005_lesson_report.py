# Generated by Django 4.2.7 on 2023-11-24 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("summery", "0004_lesson_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="report",
            field=models.FileField(null=True, upload_to="reports/"),
        ),
    ]
