import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vehicles", "0002_generation_body_type_trim_specs"),
    ]

    operations = [
        migrations.AddField(
            model_name="generation",
            name="photo",
            field=models.ImageField(blank=True, upload_to="catalog/generations/"),
        ),
    ]
