import logging
import requests
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from celery import shared_task


@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report (customers, orders, revenue)
    and logs it with a timestamp.
    """
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # GraphQL query
        query = gql("""
        query {
            totalCustomers
            totalOrders
            totalRevenue
        }
        """)

        response = client.execute(query)

        total_customers = response.get("totalCustomers", 0)
        total_orders = response.get("totalOrders", 0)
        total_revenue = response.get("totalRevenue", 0.0)

        # Log the report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = (
            f"{timestamp} - Report: "
            f"{total_customers} customers, "
            f"{total_orders} orders, "
            f"{total_revenue} revenue\n"
        )

        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(log_line)

        logging.info("CRM weekly report generated successfully.")

    except Exception as e:
        logging.error(f"Error generating CRM report: {e}")
