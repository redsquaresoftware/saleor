import requests
from django.conf import settings
from .utils import safe_get
from saleor.account.models import User

# from .fragments import use_fragment, page_info_fragment

saleor_url = settings.SALEOR_GRAPHQL_URL

# saleor's app auth header
auth_header = {"Authorization": f"Bearer {settings.COGNITO_AUTH_LAYER_APP_TOKEN}"}


# standardize method to send graphql request
def send_graphql_request(query, variables):
    result = requests.post(
        saleor_url, json={"query": query, "variables": variables}, headers=auth_header,
    )
    return result.json()


# find user using "email" via direct db access instead of graphql API
# for better performance
def get_user(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


# Graphql queries
# -------------------------------


def create_new_user(email, password):
    query = """
        mutation params($email: String!, $password: String!) {
            accountRegister(input: { email: $email, password: $password }) {
                accountErrors {
                    field
                    code
                }
                user {
                    email
                    isActive
                }
            }
        }
    """
    variables = {"email": email, "password": password}

    result = send_graphql_request(query, variables)

    # try to parse and get user's email
    error = safe_get(result, "data", "accountRegister", "accountError")

    if error is not None:
        raise Exception("User cannot be registered.")


def create_saleor_access_token(email, password):
    query = """
        mutation params($email: String!, $password: String!) {
            tokenCreate(email: $email, password: $password) {
                token
                refreshToken
                csrfToken
                user {
                    email
                }
                errors {
                    field
                    message
                }
            }
        }
    """
    variables = {"email": email, "password": password}

    result = send_graphql_request(query, variables)

    # try to parse and get token
    token = safe_get(result, "data", "tokenCreate", "token")

    if token is None:
        raise Exception("User's token cannot be generated.")

    return token


# # check whether user exists in Saleor account db
# def has_user(email):
#     # define user search query
#     query = use_fragment(
#         """
#         query SearchCustomers($after: String, $first: Int!, $query: String!) {
#             search: customers(after: $after, first: $first, filter: { search: $query }) {
#                 edges {
#                     node {
#                         id
#                         email
#                     }
#                 }
#                 pageInfo {
#                     ...PageInfoFragment
#                 }
#             }
#         }
#         """,
#         page_info_fragment,
#     )
#     # set user's email as search filter & only get one result
#     variables = {"after": None, "first": 1, "query": email}

#     result = send_graphql_request(query, variables)

#     # try to parse and get user's email
#     user = safe_get(result, "data", "search", "edges", 0, "node", "email")

#     # return true only if email exists
#     return True if user is not None and user != "" else False
