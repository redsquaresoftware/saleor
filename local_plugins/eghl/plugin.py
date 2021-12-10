from django.http import HttpResponse
from saleor.celeryconf import app
from saleor.plugins.base_plugin import BasePlugin
from cognito_auth.utils import safe_get
from .api import checkout_payment_create, checkout_complete, update_payment_on_django
from local_plugins.cms.plugin import process_order_on_django, save_order_metadata
from local_plugins.receipting.api import invoice_request_for_order

EGHL_TRANSACTION_SUCCESS_CODE = "0"
EGHL_TRANSACTION_FAILURE_CODE = "1"


class eGHLPaymentGatewayPlugin(BasePlugin):
    PLUGIN_ID = "local_plugins.eghl.plugin"
    PLUGIN_NAME = "eGHL Payment Gateway"
    DEFAULT_ACTIVE = True

    def webhook(self, request, path, previous_value):
        print("Webhook Triggered: local_plugins.eghl.plugin", path)

        # run it as a background celery task so that it returns OK response
        # straight away as eGHL wanted
        process_transaction.delay(request.POST.dict())

        return HttpResponse(content="OK")


@app.task()
def process_transaction(request_body):

    # extract values from body
    body = request_body
    token = body.get("Param6")
    agent = body.get("Param7")
    amount = body.get("Amount")
    payment_id = body.get("PaymentID")
    payment_method = body.get("PymtMethod")
    credit_card = body.get("CardNoMask")
    status = str(body.get("TxnStatus"))

    # for checking if transaction processing is successful or not
    success = False

    try:
        # make sure eghl transaction is successful
        if status == EGHL_TRANSACTION_SUCCESS_CODE:

            # use dummy payment gateway to mock payment for checkout on saleor
            # raises exception if any error found from response
            checkout_payment_create(token, amount, credit_card)

            # closes checkout and create an order
            # raises exception if any error found from response
            data = checkout_complete(token)

            # lastly, we can update payment status on Django so that we can keep track
            order_id = safe_get(data, "order", "id")
            success = update_payment_on_django(payment_id, order_id, is_success=True)

        # transaction failed or not found
        else:
            raise Exception(
                f"Transaction is not successful for {payment_id} - status: {status}"
            )

    # anything failed, log it then update payment status as failed
    except Exception as e:
        print("EXCEPTION IN eGHL Webhook: ", e)

        # only update if payment id can be found in the request
        if payment_id:
            update_payment_on_django(payment_id, order_id=None, is_success=False)

    # only process order to add ads packages/addons to django if everything goes well
    if success:
        process_order_on_django(order_id=order_id)

        # save payment id & agent name as it's needed to generate invoice/receipt
        save_order_metadata(
            order_id=order_id,
            agent_name=agent,
            payment_id=payment_id,
            payment_method=payment_method,
        )

        # auto-generate invoice & receipt only after payment id & agent name are saved
        invoice_request_for_order(order_id=order_id)

