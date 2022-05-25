from django.db import models
from saleor.account.models import User


class CognitoUserJwt(models.Model):
    class Meta:
        indexes = [models.Index(fields=["email",])]

    email = models.ForeignKey(
        User, to_field="email", null=False, on_delete=models.CASCADE
    )
    saleor_jwt = models.TextField()

