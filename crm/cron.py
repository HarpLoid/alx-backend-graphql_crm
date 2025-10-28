#!/usr/bin/env python3
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Logs a heartbeat message to /tmp/crm_heartbeat_log.txt
    and optionally checks if the GraphQL endpoint responds.
    """
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Message to log
    message = f"{timestamp} CRM is alive\n"

    # Append to the log file
    with open(log_file, "a") as f:
        f.write(message)

    # Optional: Verify the GraphQL endpoint
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=2,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ hello }")
        response = client.execute(query)
        print(f"GraphQL endpoint responded: {response}")
    except Exception as e:
        print(f"GraphQL check failed: {e}")

def update_low_stock():
    """
    Runs the UpdateLowStockProducts GraphQL mutation
    and logs the updated products to /tmp/low_stock_updates_log.txt.
    """
    log_file = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Define and execute the mutation
        mutation = gql("""
        mutation {
          updateLowStockProducts {
            success
            message
            updatedProducts {
              name
              stock
            }
          }
        }
        """)

        result = client.execute(mutation)
        data = result.get("updateLowStockProducts", {})

        # Log results
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {data.get('message')}\n")
            for p in data.get("updatedProducts", []):
                f.write(f" - {p['name']}: stock = {p['stock']}\n")

        print("Low-stock products updated successfully.")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] ERROR: {e}\n")
        print(f"Error running low-stock update: {e}")

