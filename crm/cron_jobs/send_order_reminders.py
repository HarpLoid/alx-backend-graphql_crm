#!/usr/bin/env python3
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Log file
LOG_FILE = "/tmp/order_reminders_log.txt"

# Configure the transport and client
transport = RequestsHTTPTransport(
    url=GRAPHQL_URL,
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=False)

# Calculate the date range (last 7 days)
today = datetime.now()
seven_days_ago = today - timedelta(days=7)

# Define GraphQL query
query = gql("""
query RecentOrders($fromDate: DateTime!) {
  allOrders(filter: { orderDate_Gte: $fromDate }) {
    id
    customer {
      email
    }
  }
}
""")

# Execute the query
result = client.execute(query, variable_values={"fromDate": seven_days_ago.isoformat()})

# Extract and log the results
orders = result.get("allOrders", [])

with open(LOG_FILE, "a") as log:
    for order in orders:
        order_id = order.get("id")
        email = order.get("customer", {}).get("email")
        log.write(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] Order ID: {order_id}, Email: {email}\n")

print("Order reminders processed!")
