# Generated by Django 4.2.5 on 2023-10-08 14:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0011_alter_bid_options_listing_winner"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="sold_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=8, null=True
            ),
        ),
    ]
