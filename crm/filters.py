import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    phone_starts_with = django_filters.CharFilter(method='filter_phone_starts_with')
    
    def filter_phone_starts_with(self, queryset, name, value):
        """Custom filter for phone numbers starting with a specific prefix (e.g., +1)."""
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset

    class Meta:
        model = Customer
        fields = [
            'name',
            'email',
            'created_at__gte',
            'created_at__lte'
        ]

class ProductFilter(django_filters.FilterSet):
    
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    low_stock = django_filters.NumberFilter(method='low_stock')
    
    def low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=value)
        return queryset

    class Meta:
        model = Product
        fields = [
            'name',
            'price__gte',
            'price__lte',
            'stock__gte',
            'stock__lte'
        ]

class OrderFilter(django_filters.FilterSet):
    
    total_amount__gte = django_filters.NumberFilter(method='filter_total_amount_gte')
    total_amount__lte = django_filters.NumberFilter(method='filter_total_amount_lte')
    order_date__gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date__lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    product_id = django_filters.NumberFilter(method='filter_by_product_id')

    class Meta:
        model = Order
        fields = [
            'order_date__gte',
            'order_date__lte',
            'customer_name',
            'product_name'
        ]
    
    def filter_total_amount_gte(self, queryset, name, value):
        ids = [order.id for order in queryset if order.total_amount >= value]
        return queryset.filter(id__in=ids)

    def filter_total_amount_lte(self, queryset, name, value):
        ids = [order.id for order in queryset if order.total_amount <= value]
        return queryset.filter(id__in=ids)
    
    def filter_by_product_id(self, queryset, name, value):
        """
        Filters orders that include a specific product ID.
        """
        if value is not None:
            return queryset.filter(order_items__product__id=value).distinct()
        return queryset
