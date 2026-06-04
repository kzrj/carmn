# Generated manually for parser, analytics, and favorites fields

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("sold", "Sold"),
                    ("moderation", "Moderation"),
                    ("archived", "Archived"),
                ],
                default="active",
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name="listing",
            name="source",
            field=models.CharField(
                choices=[
                    ("user", "User"),
                    ("unegui", "Unegui"),
                    ("facebook", "Facebook"),
                    ("dealer", "Dealer"),
                ],
                default="user",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="listing",
            name="external_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="listing",
            name="external_url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="listing",
            name="parsed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="listing",
            name="vin",
            field=models.CharField(blank=True, db_index=True, default="", max_length=17),
        ),
        migrations.AddField(
            model_name="listing",
            name="chassis_number",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.AddField(
            model_name="listing",
            name="view_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="listing",
            name="price_usd",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Original price in USD, if specified",
                max_digits=12,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="ListingPriceHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("old_price", models.PositiveBigIntegerField()),
                ("new_price", models.PositiveBigIntegerField()),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="listing_price_changes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="price_history",
                        to="listings.listing",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "listing price histories",
                "ordering": ["-changed_at"],
            },
        ),
        migrations.CreateModel(
            name="UserFavorite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorited_by",
                        to="listings.listing",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorite_listings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ListingView",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ip_hash", models.CharField(blank=True, default="", max_length=64)),
                ("viewed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="views",
                        to="listings.listing",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="listing_views",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-viewed_at"],
            },
        ),
        migrations.AddIndex(
            model_name="listing",
            index=models.Index(fields=["-view_count"], name="listings_li_view_co_idx"),
        ),
        migrations.AddIndex(
            model_name="listing",
            index=models.Index(fields=["source"], name="listings_li_source_idx"),
        ),
        migrations.AddIndex(
            model_name="listingview",
            index=models.Index(fields=["listing", "-viewed_at"], name="listings_li_listing_idx"),
        ),
        migrations.AddIndex(
            model_name="listingview",
            index=models.Index(fields=["listing", "ip_hash", "-viewed_at"], name="listings_li_list_ip_idx"),
        ),
        migrations.AddConstraint(
            model_name="listing",
            constraint=models.UniqueConstraint(
                condition=~Q(external_id=""),
                fields=("source", "external_id"),
                name="uniq_listing_source_external_id",
            ),
        ),
        migrations.AddConstraint(
            model_name="listing",
            constraint=models.UniqueConstraint(
                condition=~Q(vin=""),
                fields=("vin",),
                name="uniq_listing_vin_nonempty",
            ),
        ),
        migrations.AddConstraint(
            model_name="userfavorite",
            constraint=models.UniqueConstraint(
                fields=("user", "listing"),
                name="uniq_user_favorite_listing",
            ),
        ),
    ]
