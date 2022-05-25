# Include this to the end of your saleor's setting file
import os
import json
from urllib import request

# ...

# Change this manually!
# --------------------------------------

# Change the default value from True to False
# ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL = get_bool_from_env(
#     "ENABLE_ACCOUNT_CONFIRMATION_BY_EMAIL", False
# )

# INSTALLED_APPS = [
# ...
# "cognito_auth.apps.CognitoAuthLayerConfig",
# ...
# ]

# Cognito Integration
# --------------------------------------

# aws cognito integration
COGNITO_AWS_REGION = os.environ.get("COGNITO_AWS_REGION")
COGNITO_USER_POOL = os.environ.get("COGNITO_USER_POOL")
# Provide this value if `id_token` is used for authentication (it contains 'aud' claim).
# `access_token` doesn't have it, in this case keep the COGNITO_AUDIENCE empty
COGNITO_AUDIENCE = None
COGNITO_POOL_URL = (
    None  # will be set few lines of code later, if configuration provided
)
rsa_keys = {}
# To avoid circular imports, we keep this logic here.
# On django init we download jwks public keys which are used to validate jwt tokens.
# For now there is no rotation of keys (seems like in Cognito decided not to implement it)
if COGNITO_AWS_REGION and COGNITO_USER_POOL:
    COGNITO_POOL_URL = "https://cognito-idp.{}.amazonaws.com/{}".format(
        COGNITO_AWS_REGION, COGNITO_USER_POOL
    )
    pool_jwks_url = COGNITO_POOL_URL + "/.well-known/jwks.json"
    jwks = json.loads(request.urlopen(pool_jwks_url).read())
    rsa_keys = {key["kid"]: json.dumps(key) for key in jwks["keys"]}

# core jwt auth handler
COGNITO_JWT_AUTH = {
    "PUBLIC_KEY": rsa_keys,
    "ALGORITHM": "RS256",
    "AUDIENCE": COGNITO_AUDIENCE,
    "ISSUER": COGNITO_POOL_URL,
    "AUTH_HEADER_PREFIX": "Bearer",
}

COGNITO_AUTH_APP_TOKEN = os.environ.get("COGNITO_AUTH_APP_TOKEN")
COGNITO_AUTH_USER_PASSWORD = os.environ.get("COGNITO_AUTH_USER_PASSWORD")

# Saleor Integration
# --------------------------------------

SALEOR_GRAPHQL_URL = os.environ.get("SALEOR_GRAPHQL_URL")
