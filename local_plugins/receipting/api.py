import requests
from cognito_auth.utils import safe_get
from django.conf import settings

saleor_url = settings.SALEOR_GRAPHQL_URL

# reuse cognito auth app token
auth_header = {"Authorization": f"Bearer {settings.COGNITO_AUTH_APP_TOKEN}"}


# standardize method to send graphql request
def send_graphql_request(query, variables):
    return requests.post(
        saleor_url, json={"query": query, "variables": variables}, headers=auth_header,
    ).json()


# Graphql queries
# -------------------------------


def invoice_request(order_id):
    query = """
        mutation params($orderId: ID!) {
            invoiceRequest(orderId: $orderId) {
                errors {
                    field
                    message
                    code
                }
            }
        }
    """
    variables = {"orderId": order_id}

    result = send_graphql_request(query, variables)

    # check if there's any error
    result = safe_get(result, "data", "invoiceRequest")
    error = safe_get(result, "errors")

    if error is not None and len(error) != 0:
        raise Exception(f"Invoice cannot be requested: {order_id}")

    return result
