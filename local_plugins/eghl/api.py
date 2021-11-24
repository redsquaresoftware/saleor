import requests
from cognito_auth.utils import safe_get
from django.conf import settings

saleor_url = settings.SALEOR_GRAPHQL_URL
django_url = settings.DJANGO_GRAPHQL_URL

# reuse cognito auth app token
auth_header = {"Authorization": f"Bearer {settings.COGNITO_AUTH_APP_TOKEN}"}


# standardize method to send graphql request
def send_graphql_request(query, variables):
    return requests.post(
        saleor_url, json={"query": query, "variables": variables}, headers=auth_header,
    ).json()


def send_django_graphql_request(query, variables):
    return requests.post(
        django_url, json={"query": query, "variables": variables}
    ).json()


# Graphql queries
# -------------------------------


def checkout_payment_create(token, amount, credit_card):
    # fixed gateway
    gateway = "mirumee.payments.dummy"

    query = """
        mutation params($token: UUID, $gateway: String!, $amount: PositiveDecimal, $creditCard: String) {
            checkoutPaymentCreate(token: $token, input: { gateway: $gateway, amount: $amount, token: $creditCard }) {
                payment {
                    id
                    order {
                        id
                        created
                        statusDisplay
                        paymentStatusDisplay
                        isPaid
                    }
                }
                errors {
                    field
                    message
                }
            }
        }
    """
    variables = {
        "token": token,
        "gateway": gateway,
        "amount": amount,
        "creditCard": credit_card,
    }

    result = send_graphql_request(query, variables)

    # check if there's any error
    result = safe_get(result, "data", "checkoutPaymentCreate")
    error = safe_get(result, "errors")

    if error is not None and len(error) != 0:
        raise Exception(f"Checkout Payment cannot be created - {token}: ", error)

    return result


def checkout_complete(token):
    query = """
        mutation params($token: UUID) {
            checkoutComplete(token: $token) {
                confirmationNeeded
                confirmationData
                order {
                    id
                    isPaid
                    statusDisplay
                }
                errors {
                    field
                    message
                    code
                }
            }
        }
    """
    variables = {"token": token}

    result = send_graphql_request(query, variables)

    # check if there's any error
    result = safe_get(result, "data", "checkoutComplete")
    error = safe_get(result, "errors")

    if error is not None and len(error) != 0:
        raise Exception(f"Checkout cannot be completed - {token}: ", error)

    return result


def update_payment_on_django(payment_id, order_id, is_success):
    print(
        f"Sending Payment Update request to Django - PaymentID: {payment_id} | OrderID: {order_id} | Success: {is_success}"
    )

    query = f"""
        mutation params($paymentId: ID!, {"$orderId: ID," if order_id else ""} $isSuccess: Boolean!) {{
            updatePayment(input: {{paymentId: $paymentId, {"orderId: $orderId," if order_id else ""} isSuccess: $isSuccess}}) {{
                ok
                error
            }}
        }}
    """
    variables = {
        "paymentId": payment_id,
        "isSuccess": is_success,
    }

    if order_id:
        variables["orderId"] = order_id

    # check if there's any error
    result = send_django_graphql_request(query, variables)
    error = safe_get(result, "data", "error")

    if error is not None:
        raise Exception(f"Payment cannot be updated - {payment_id}: ", error)

    # true indicate update success
    return True
