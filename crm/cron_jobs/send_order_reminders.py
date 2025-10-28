#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Log file
LOG_FILE = "/tmp/order_reminders_log.txt"

# Calculate the date range (last 7 days)
today = datetime.now()
seven_days_ago = today - timedelta(days=7)

# GraphQL query
query = """
query RecentOrders($fromDate: DateTime!) {
  allOrders(filter: { orderDate_Gte: $fromDate }) {
    id
    customer {
      email
    }
  }
}
"""

# Send the request
response = requests.post(
    GRAPHQL_URL,
    json={
        "query": query,
        "variables": {"fromDate": seven_days_ago.isoformat()}
    },
)

# Check response
if response.status_code == 200:
    data = response.json()
    orders = data.get("data", {}).get("allOrders", [])
    
    # Log each order
    with open(LOG_FILE, "a") as log:
        for order in orders:
            order_id = order.get("id")
            email = order.get("customer", {}).get("email")
            log.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] Order ID: {order_id}, Email: {email}\n")

    print("Order reminders processed!")
else:
    print(f"Failed to fetch orders. Status code: {response.status_code}")
