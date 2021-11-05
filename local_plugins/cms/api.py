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
    email, order_id, start_date, end_date, ads_number, is_unlimited_ads, sales_amount
):
    query = """
        mutation params($email: String!, $orderId: ID!, $startDate: DateTime!, $endDate: DateTime!, $adsNumber: Int, $isUnlimitedAds: Boolean, $salesAmount: Float!) {
            createAdsPackage(input: { email: $email, orderId: $orderId, startDate: $startDate, endDate: $endDate, adsNumber: $adsNumber, isUnlimitedAds: $isUnlimitedAds, salesAmount: $salesAmount }) {
                ok
                error
            }
        }
    """
    variables = {
        "email": email,
        "orderId": order_id,
        "startDate": start_date,
        "endDate": end_date,
        "adsNumber": ads_number,
        "isUnlimitedAds": is_unlimited_ads,
        "salesAmount": sales_amount,
    }

    result = send_graphql_request(query, variables)

    # try to parse and get user's email
    error = safe_get(result, "data", "createAdsPackage", "error")

    if error is not None:
        print("Error in creating Ads Package, full response: ", result)
        raise Exception("Ads Package cannot be created for user: ", email)

