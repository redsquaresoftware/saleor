from django.http import HttpResponse
from saleor.plugins.base_plugin import BasePlugin
from cognito_auth.utils import safe_get
from .api import checkout_payment_create, checkout_complete, update_payment_on_django
from local_plugins.cms.plugin import process_order

EGHL_TRANSACTION_SUCCESS_CODE = "0"
EGHL_TRANSACTION_FAILURE_CODE = "1"


class eGHLPaymentGatewayPlugin(BasePlugin):
    PLUGIN_ID = "local_plugins.eghl.plugin"
    PLUGIN_NAME = "eGHL Payment Gateway"
    DEFAULT_ACTIVE = True

    def webhook(self, request, path, previous_value):
        print("local_plugins.eghl.plugin Webhook Triggered at path: ", path)

        # extract values from body
        body = request.POST.dict()
        token = body.get("Param6")
        amount = body.get("Amount")
        payment_id = body.get("PaymentID")
        credit_card = body.get("CardNoMask")

        try:
            # make sure eghl transaction is successful
            if str(body.get("TxnStatus")) == EGHL_TRANSACTION_SUCCESS_CODE:

                # use dummy payment gateway to mock payment for checkout on saleor
                # raises exception if any error found from response
                checkout_payment_create(token, amount, credit_card)

                # closes checkout and create an order
                # raises exception if any error found from response
                data = checkout_complete(token)

                # lastly, we can update payment status on Django so that we can keep track
                order_id = safe_get(data, "order", "id")
                success = update_payment_on_django(
                    payment_id, order_id, is_success=True
                )

                # only process order to add ads packages/addons to django if everything goes well
                if success:
                    process_order(order_id)

            # transaction failed or not found
            else:
                # only update if payment id can be found in the request
                if payment_id:
                    update_payment_on_django(
                        payment_id, order_id=None, is_success=False
                    )

            return HttpResponse(content="OK")

        # anything failed, log it then update payment status as failed
        except Exception as e:
            print("EXCEPTION IN eGHL Webhook: ", e)

            if payment_id:
                update_payment_on_django(payment_id, order_id=None, is_success=False)

            return HttpResponse(content="OK")
