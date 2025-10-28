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
