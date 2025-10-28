#!/bin/bash

LOG_FILE="/tmp/customer_cleanup_log.txt"

timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

{
    echo "[$(timestamp)] Starting inactive customer cleanup..."
    python manage.py shell <<'EOF'
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer, Order

# Define the cutoff date (1 year ago)
cutoff = timezone.now() - timedelta(days=365)

# Find customers who have NOT made any orders since the cutoff
inactive_customers = Customer.objects.exclude(
    id__in=Order.objects.filter(created_at__gte=cutoff).values('customer_id')
)

count = inactive_customers.count()

print(f"Cleanup run at: {timezone.now()}")
print(f"Found {count} inactive customers...")

if count > 0:
    inactive_customers.delete()
    print(f"Deleted {count} inactive customers.")
else:
    print("No inactive customers found.")
EOF
    echo "[$(timestamp)] ✨ Cleanup completed."
} >> "$LOG_FILE" 2>&1
