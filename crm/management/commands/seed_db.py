import random
from django.core.management.base import BaseCommand
from django_seed import Seed
from faker import Faker
from datetime import timezone

from crm.models import Customer, Product, Order

fake = Faker()


class Command(BaseCommand):
    help = "Seeds the database with sample Customers, Products, and Orders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--customers",
            type=int,
            default=10,
            help="Number of customers to create (default: 10)"
        )
        parser.add_argument(
            "--products",
            type=int,
            default=8,
            help="Number of products to create (default: 8)"
        )
        parser.add_argument(
            "--orders",
            type=int,
            default=15,
            help="Number of orders to create (default: 15)"
        )

    def handle(self, *args, **options):
        seeder = Seed.seeder()

        num_customers = options["customers"]
        num_products = options["products"]
        num_orders = options["orders"]

        self.stdout.write(self.style.WARNING("Starting database seeding..."))

        # 1 Seed Customers
        seeder.add_entity(Customer, num_customers, {
            "name": lambda x: fake.name(),
            "email": lambda x: fake.unique.email(),
            "phone": lambda x: fake.phone_number(),
        })

        # 2 Seed Products
        seeder.add_entity(Product, num_products, {
            "name": lambda x: fake.word().capitalize(),
            "price": lambda x: round(random.uniform(10, 500), 2),
            "stock": lambda x: random.randint(5, 100),
        })

        # Execute seeder for Customers & Products
        inserted = seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"Created {num_customers} customers and {num_products} products."))

        customers = list(Customer.objects.all())
        products = list(Product.objects.all())

        # 3 Create sample Orders manually
        if not customers or not products:
            self.stdout.write(self.style.ERROR("Skipping order creation — missing customers or products."))
            return

        self.stdout.write(self.style.WARNING(f"Creating {num_orders} sample orders..."))
        for _ in range(num_orders):
            customer = random.choice(customers)
            order = Order.objects.create(
                customer=customer,
                order_date=fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc)
            )
            # Randomly associate between 1–3 products
            selected_products = random.sample(products, random.randint(1, min(3, len(products))))
            order.products.set(selected_products)
            order.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {num_orders} orders!"))
        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))
