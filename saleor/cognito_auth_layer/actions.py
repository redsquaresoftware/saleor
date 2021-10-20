from django.conf import settings
from .models import CognitoUserJwt
from .api import get_user, create_new_user, create_saleor_access_token

# note: all users will have the same password as given in the settings file
user_password = settings.COGNITO_AUTH_LAYER_USER_PASSWORD


def get_saleor_jwt(email):
    try:
        # try and find user account in db
        user = get_user(email)

        # create a new saleor account for the user if not found
        if user is None:
            create_new_user(email, user_password)
            user = get_user(email)

        # try and get user's saleor jwt from db
        mapped = None
        try:
            mapped = CognitoUserJwt.objects.get(email=user)

        # user hasn't had a saleor jwt generated and mapped to them
        # hence logs user onto saleor to get their access token then save it into db
        # note: saleor jwt is configured to not expire ever, hence we can save and
        #       use it indefinitely
        except CognitoUserJwt.DoesNotExist:
            access_token = create_saleor_access_token(email, user_password)
            mapped = CognitoUserJwt(email=user, saleor_jwt=access_token)
            mapped.save()

        return mapped.saleor_jwt

    except Exception as e:
        print("Error in get_saleor_jwt: ", e)
        return None
