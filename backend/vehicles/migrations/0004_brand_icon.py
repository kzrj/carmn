# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0003_generation_photo"),
    ]

    operations = [
        migrations.AddField(
            model_name="brand",
            name="icon",
            field=models.ImageField(blank=True, upload_to="catalog/brands/"),
        ),
    ]
