# import requests
# from cognito_auth.utils import safe_get
# from django.conf import settings

# saleor_url = settings.SALEOR_GRAPHQL_URL

# # reuse cognito auth app token
# auth_header = {"Authorization": f"Bearer {settings.COGNITO_AUTH_APP_TOKEN}"}


# # standardize method to send graphql request
# def send_graphql_request(query, variables):
#     return requests.post(
#         saleor_url, json={"query": query, "variables": variables}, headers=auth_header,
#     ).json()


# # Graphql queries
# # -------------------------------


# def invoice_request(token, amount, credit_card):
#     query = """
#         mutation params($orderId: ID!, $gateway: String!, $amount: PositiveDecimal, $creditCard: String) {
#             checkoutPaymentCreate(token: $token, input: { gateway: $gateway, amount: $amount, token: $creditCard }) {
#                 payment {
#                     id
#                     order {
#                         id
#                         created
#                         statusDisplay
#                         paymentStatusDisplay
#                         isPaid
#                     }
#                 }
#                 errors {
#                     field
#                     message
#                 }
#             }
#         }
#     """
#     variables = {
#         "token": token,
#         "gateway": gateway,
#         "amount": amount,
#         "creditCard": credit_card,
#     }

#     result = send_graphql_request(query, variables)

#     # check if there's any error
#     result = safe_get(result, "data", "checkoutPaymentCreate")
#     error = safe_get(result, "errors")

#     if error is not None and len(error) != 0:
#         raise Exception(f"Checkout Payment cannot be created - {token}: ", error)

#     return result
