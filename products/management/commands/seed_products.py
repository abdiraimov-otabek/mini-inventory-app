from decimal import Decimal
from random import uniform

from django.core.management.base import BaseCommand

from products.models import Product


PRODUCT_CATALOG = [
    "Sea Salt Caramels",
    "Dark Chocolate Hazelnuts",
    "Milk Chocolate Truffles",
    "Peanut Butter Bites",
    "Sour Raspberry Gummies",
    "Rainbow Lollipops",
    "Mini Marshmallow Packs",
    "Vanilla Fudge Squares",
    "Almond Toffee Crunch",
    "Gummy Bear Mix",
    "Assorted Macarons",
    "Chocolate Covered Espresso Beans",
    "Fruit Leather Strips",
    "Honey Roasted Cashews",
    "Maple Pecan Brittle",
    "Caramel Popcorn Bags",
    "Peppermint Bark",
    "Strawberry Cream Taffy",
    "Chocolate Chip Cookies",
    "Cocoa Powder Tin",
    "Baking Soda Canister",
    "Sea Salt Grinder",
    "Herb Scissors",
    "Stainless Mixing Bowls",
    "Silicone Spatula Set",
    "Cast Iron Skillet",
    "Reusable Piping Bags",
    "Decorative Sprinkles Mix",
    "Vanilla Bean Paste",
    "Organic Cane Sugar",
    "Brownie Mix Pouches",
    "Mini Rolling Pins",
    "Kitchen Shears",
    "Rechargeable Batteries AA (8 pack)",
    "Rechargeable Batteries AAA (8 pack)",
    "Colorful Measuring Spoons",
    "Mini Storage Jars",
    "Ceramic Dessert Plates",
    "Reusable Bento Boxes",
    "Lunch Bag Coolers",
    "Kid-Friendly Water Bottles",
    "Silicone Ice Pop Molds",
    "Chocolate Drizzle Sauce",
    "Butterscotch Syrup",
    "Whipped Cream Chargers",
    "Decorative Gift Tins",
    "Party Favor Bags",
    "Confetti Cupcake Kits",
    "Chocolate Fountain Refills",
]


class Command(BaseCommand):
    help = "Populate the database with a curated catalog of confectionary and kitchen inventory items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=len(PRODUCT_CATALOG),
            help="Number of products to seed (default: full catalog).",
        )

    def handle(self, *args, **options):
        target_count = options["count"]
        created = 0

        names = PRODUCT_CATALOG.copy()
        while len(names) < target_count:
            names.append(f"Gourmet Treat #{len(names) + 1}")

        for name in names[:target_count]:
            price = round(uniform(2.5, 120.0), 2)
            obj, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "price": Decimal(str(price)),
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {created} product(s) out of requested {target_count}.")
        )
