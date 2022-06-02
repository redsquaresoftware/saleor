import requests
from .utils import safe_get
from django.conf import settings

django_url = settings.DJANGO_GRAPHQL_URL

# django's app auth header
# auth_header = {"Authorization": f"Bearer {settings.COGNITO_AUTH_APP_TOKEN}"}
auth_header = {}


# standardize method to send graphql request
def send_graphql_request(query, variables):
    result = requests.post(
        django_url, json={"query": query, "variables": variables}, headers=auth_header,
    )
    return result.json()


# Graphql queries
# -------------------------------


def create_ads_package(
    name, 
    email, 
    order_id, 
    start_date, 
    end_date, 
    ads_number, 
    is_unlimited_ads, 
    quantity,
    display_name
):
    print(
        f"Sending Ads Package Create request to Django - Email: {email} | OrderID: {order_id}"
    )

    query = """
        mutation params($name: String!, $email: String!, $orderId: ID!, $startDate: DateTime!, $endDate: DateTime!, $adsNumber: Int, $isUnlimitedAds: Boolean, $quantity: Int!, $displayName: String) {
            createAdsPackage(input: { name: $name, email: $email, orderId: $orderId, startDate: $startDate, endDate: $endDate, adsNumber: $adsNumber, isUnlimitedAds: $isUnlimitedAds, quantity: $quantity, displayName: $displayName }) {
                ok
                error
            }
        }
    """
    variables = {
        "name": name,
        "email": email,
        "orderId": order_id,
        "startDate": start_date,
        "endDate": end_date,
        "adsNumber": ads_number,
        "isUnlimitedAds": is_unlimited_ads,
        "quantity": quantity,
        "displayName": display_name
    }

    result = send_graphql_request(query, variables)

    # try to parse and get user's email
    error = safe_get(result, "data", "createAdsPackage", "error")

    if error is not None and len(error) != 0:
        print("Error in creating Ads Package, full response: ", result)
        raise Exception("Ads Package cannot be created for user: ", email)


def create_add_on(order_id, add_ons):
    print(f"Sending Add On Create request to Django - OrderID: {order_id}")

    query = """
        mutation params($orderId: ID!, $addOnInput: [AddOnInput]) {
            createAddOn(input: { orderId: $orderId, addOnInput: $addOnInput }) {
                ok
                error
            }
        }
    """

    variables = {
        "orderId": order_id,
        "addOnInput": [
            {
                "addOnType": safe_get(x, "add_on_type"),
                "region": safe_get(x, "region"),
                "addOnDuration": safe_get(x, "add_on_duration"),
                "quantity": safe_get(x, "quantity"),
            }
            for x in add_ons
        ],
    }

    result = send_graphql_request(query, variables)

    # try to parse and get user's email
    error = safe_get(result, "data", "createAddOn", "error")

    if error is not None and len(error) != 0:
        print("Error in creating Add On, full response: ", result)
        raise Exception("Add On cannot be created for order: ", order_id)


def post_payment_listing_hook(payment_id):
    print(f"Sending Post Payment Listing Hook request to Django - PaymentID: {payment_id}")

    query = """
        mutation params($paymentId: ID!) {
            postPaymentListingHook(input: { paymentId: $paymentId }) {
                ok
                error
            }
        }
    """

    variables = {"paymentId": payment_id}

    result = send_graphql_request(query, variables)

    # try to parse and get user's email
    error = safe_get(result, "data", "postPaymentListingHook", "error")

    if error is not None and len(error) != 0:
        print("Error in Post Payment Listing Hook request, full response: ", result)
        raise Exception("Add On cannot be created for order: ", payment_id)