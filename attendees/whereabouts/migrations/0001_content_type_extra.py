from django.contrib.contenttypes.models import ContentType
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('whereabouts', '0000_initial'),
        ('contenttypes', '0002_remove_content_type_name'),

    ]

    operations = [
        migrations.RunSQL(
            sql=f"""
                ALTER TABLE {ContentType.objects.model._meta.db_table} ADD COLUMN genres VARCHAR(100) DEFAULT NULL;
                ALTER TABLE {ContentType.objects.model._meta.db_table} ADD COLUMN endpoint VARCHAR(100) DEFAULT NULL;
                CREATE INDEX django_content_genres
                   ON {ContentType.objects.model._meta.db_table} (genres);
                """,
            # reverse_sql="",
        ),
    ]
