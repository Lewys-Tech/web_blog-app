from django.contrib.postgres.operations import TrigramExtension

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogsite', '0005_post_tags'),
    ]

    operations = [ TrigramExtension()
    ]
