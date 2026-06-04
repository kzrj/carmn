import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("references", "0001_initial"),
        ("vehicles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="generation",
            name="body_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="generations",
                to="references.bodytype",
            ),
        ),
        migrations.AddField(
            model_name="trim",
            name="body_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="trims",
                to="references.bodytype",
            ),
        ),
        migrations.AddField(
            model_name="trim",
            name="drive",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="trims",
                to="references.drivetype",
            ),
        ),
        migrations.AddField(
            model_name="trim",
            name="fuel",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="trims",
                to="references.fueltype",
            ),
        ),
        migrations.AddField(
            model_name="trim",
            name="transmission",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="trims",
                to="references.transmissiontype",
            ),
        ),
    ]
