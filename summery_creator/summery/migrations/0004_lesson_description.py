# Generated by Django 4.2.7 on 2023-11-24 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("summery", "0003_alter_glossaryentry_options_alter_lesson_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="description",
            field=models.TextField(null=True),
        ),
    ]
