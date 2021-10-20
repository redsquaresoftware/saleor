from django.http.response import JsonResponse
from saleor.graphql.views import GraphQLView

from .jwt import convert_cognito_jwt_to_saleor_jwt_from_request

# --- credit ---
# author: abaskov
# reference: https://github.com/graphql-python/graphene-django/issues/345


class AuthenticatedGraphQLView(GraphQLView):
    # intercepts request first before passing it back to GraphQLView
    def dispatch(self, request, *args, **kwargs):
        try:
            # try and get get user's saleor jwt from db, create new account & saleor jwt
            # if user not found then add it to request context
            jwt = convert_cognito_jwt_to_saleor_jwt_from_request(request)

        except:
            return JsonResponse(
                {"error": "Authorization Error", "status": 401}, status=401
            )

        # replace cognito jwt in request with the saleor jwt found
        if jwt is not None:
            request.META.update(HTTP_AUTHORIZATION=f"JWT {jwt}")

        return super().dispatch(request, *args, **kwargs)
