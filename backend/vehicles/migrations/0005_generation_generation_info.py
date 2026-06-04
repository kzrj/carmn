from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vehicles", "0004_brand_icon"),
    ]

    operations = [
        migrations.AddField(
            model_name="generation",
            name="generation_info",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
