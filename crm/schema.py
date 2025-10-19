import re
import graphene
from decimal import Decimal
from django.db import transaction, IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    # Return fields
    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        name = input.name
        email = input.email
        phone = input.phone
        # validate email
        try:
            validate_email(email)
        except ValidationError:
            return cls(
                success=False,
                message="Invalid email format.",
                customer=None
            )
        
        # Check for duplicate email
        if Customer.objects.filter(email=email).exists():
            return cls(
                success=False,
                message="Email already exists.",
                customer=None
            )
        
        # Validate phone format (if provided)
        if phone:
            pattern = r"^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$"
            if not re.match(pattern, phone):
                return cls(
                    success=False,
                    message="Invalid phone format. Use +1234567890 or 123-456-7890.",
                    customer=None
                )
        
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        
        return cls(
            success=True,
            message="Customer created successfully.",
            customer=customer
        )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput,
                                 required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    @classmethod
    def mutate(cls, root, info, input):
        created = []
        errors = []
        
        with transaction.atomic():
            for data in input:
                name = data.name
                email = data.email
                phone = data.phone
                
                if Customer.objects.filter(email=email).exists():
                    errors.append(f"{email}: already exists")
                    continue
                
                customer = Customer.objects.create(
                    name=name,
                    email=email,
                    phone=phone
                )
                created.append(customer)

        return cls(customers=created,
                   errors=errors)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)
        
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        name = input.name
        price = Decimal(str(input.price))
        stock = input.stock or 0
        
        if price < 0:
            return cls(
                success=False,
                message="Price must be positive",
                product=None
            )
        
        if stock < 0:
            return cls(
                success=False,
                message="Stock must be positive",
                product=None
            )
        
        product = Product.objects.create(
            name=name, price=price, stock=stock
        )
        
        return cls(
            success=True,
            message="Product created successfully.",
            product=product
        )

class OrderType(DjangoObjectType):
    total_amount = graphene.Decimal()
    
    class Meta:
        model = Order
        fields = ("id","customer", "products", "order_date")
    
    def resolve_total_amount(self, info):
        return self.total_amount

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.UUID(required=True)
    product_ids = graphene.List(graphene.UUID, required=True)
    order_date = graphene.DateTime()

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)
        
    order = graphene.Field(OrderType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        
        # Validate Customer
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return cls(errors=errors)
        
        # Validate product list
        if not input.product_ids:
            errors.append("At least one product must be selected.")
            return cls(errors=errors)
        
        # Gets all valid products
        products = Product.objects.filter(id__in=input.product_ids)
        if products.count() != len(input.product_ids):
            valid_ids = {str(p.id) for p in products}
            invalid_ids = [str(pid) for pid in input.product_ids if str(pid) not in valid_ids]
            errors.append(f"Invalid product IDs: {', '.join(invalid_ids)}")
            return cls(errors=errors)
        
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    order_date=input.order_date
                )
                order.products.set(products)
                
                return cls(
                    order=order,
                    message="Order created successfully",
                    errors=[]
                )
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            return cls(errors=errors)

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
