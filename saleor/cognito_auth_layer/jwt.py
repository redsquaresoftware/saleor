import jwt
from jwt import DecodeError
from jwt.algorithms import RSAAlgorithm
from django.conf import settings
from .actions import get_saleor_jwt


# --- credit ---
# author: Gleb Pushkov
# reference: https://djangostars.com/blog/bootstrap-django-app-with-cognito/
def verify_and_decode(token):
    """
    To verify the signature of an Amazon Cognito JWT, first search for the public key with a key ID that
    matches the key ID in the header of the token. (c)
    https://aws.amazon.com/premiumsupport/knowledge-center/decode-verify-cognito-json-token/
    """
    # jwt decode options
    options = {
        "verify_signature": True,
        "verify_exp": True,
    }
    # get key-id in jwt header for public key verification
    unverified_header = jwt.get_unverified_header(token)
    if "kid" not in unverified_header:
        raise DecodeError("Incorrect authentication credentials.")
    kid = unverified_header["kid"]
    try:
        # pick a proper public key according to `kid` from token header
        public_key = RSAAlgorithm.from_jwk(
            settings.COGNITO_JWT_AUTH.get("PUBLIC_KEY")[kid]
        )
    except KeyError:
        # in this place we could refresh cached jwks and try again
        raise DecodeError("Can't find proper public key in jwks")
    else:
        return jwt.decode(
            token,
            public_key,
            algorithms=[settings.COGNITO_JWT_AUTH.get("ALGORITHM")],
            options=options,
            audience=settings.COGNITO_JWT_AUTH.get("AUDIENCE"),
            issuer=settings.COGNITO_JWT_AUTH.get("ISSUER"),
        )


def is_saleor_app_token(token):
    try:
        # try and decode token, if there's no issue decoding the token
        # then it's a valid JWT token, which means it's a Cognito JWT
        # note: this works because saleor app token is just a random string
        #       and not in a valid jwt format
        jwt.decode(token, options={"verify_signature": False})
        return False
    except:
        # fail to decode token hence we can assume it's a saleor app token
        return True


def convert_cognito_jwt_to_saleor_jwt_from_request(request):
    jwt = None

    # get token from request headers
    auth_header = request.META.get("HTTP_AUTHORIZATION")

    # get user object only if the auth header is found in headers
    if auth_header is not None:
        # check if auth header prefix follows the correct format:
        # <prefix specified in the settings.py> + a trailing space
        prefix = settings.COGNITO_JWT_AUTH.get("AUTH_HEADER_PREFIX") + " "

        if auth_header.startswith(prefix) is not True:
            return jwt

        # verify & decode token
        token = auth_header[len(prefix) :]

        # early return if token is Saleor's App token but not Cognito JWT
        if is_saleor_app_token(token):
            return None

        # note: we get user's email info from 'username' attribute
        payload = verify_and_decode(token)
        email = payload.get("username")

        # get user's saleor's access token from db
        jwt = get_saleor_jwt(email)

    return jwt
