from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE web_have ADD COLUMN status VARCHAR(20) DEFAULT 'used';",
            "ALTER TABLE web_have DROP COLUMN status;"
        ),
        migrations.RunSQL(
            "ALTER TABLE web_have ADD COLUMN points INTEGER DEFAULT 99;",
            "ALTER TABLE web_have DROP COLUMN points;"
        ),
    ]