# Generated by Django 5.1.1 on 2024-09-14 12:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogsite', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-publish']},
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(max_length=250, unique=True),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['-publish'], name='blogsite_po_publish_ab442f_idx'),
        ),
    ]
