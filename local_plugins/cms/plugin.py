from datetime import datetime
from graphql_relay.node.node import from_global_id, to_global_id
from saleor.plugins.base_plugin import BasePlugin
from saleor.order.models import Order
from .api import create_ads_package, create_add_on
from local_plugins.receipting.api import invoice_request_for_order

# import all constants
from .constants import *
from .helpers import (
    get_attributes_from_product,
    get_attributes_from_add_on,
    calculate_start_and_end_date,
    preprocess_ads_number,
)


class DjangoCMSPlugin(BasePlugin):
    PLUGIN_ID = "local_plugins.cms.plugin"
    PLUGIN_NAME = "Django CMS Integration"
    DEFAULT_ACTIVE = True

    # todo: just an idea, but we might be able to implement product purchase condition check here
    # def checkout_updated(self, checkout, previous_value):
    # pass

    # initial idea: use this order fully paid hook to process and add ads packages/add-ons to
    #               listing on django, however this approach comes with serious downsides
    # 1. we don't have access to transaction data, e.g. payment_id
    # 2. we can't ensure that complete_payment_on_django will be completed before this hook is triggered
    # 3. (Side Effect) if an admin creates an order manually on dashboard, it'd break the overall payment flow
    # As a result, we need other get-around hacks to overcome this issue.
    #
    # Solution: don't use this fully-paid hook, just use a function call in eGHL plugin. this way, we can
    #           have access to the payment_id + we can always ensure the function will only be called
    #           when complete_payment_on_django is completed
    # def order_fully_paid(self, order, previous_value):
    #     # convert order object id to relay global id
    #     order_id = to_global_id(type(order).__name__, order.id)

    #     # all graphql mutation to generate both invoice & receipt straight away
    #     process_order_on_django(order_id=order_id)


# main function to use to process order and add ads package/add-on to django
# parameter: order_id must be in relay global id format
def process_order_on_django(order_id):
    try:
        # convert relay global id to object id
        _, id = from_global_id(order_id)

        # make sure order exists
        order = Order.objects.get(id=id)

        print("Order is fully paid: ", order)

        order_lines = order.lines.all()

        # for temporarily storing all add-ons
        add_ons = []

        # go through each product in the order
        for line in order_lines:

            # retrieve the actual product object from db
            product = line.variant.product
            product_type = product.product_type.name.upper()

            # for Ads Package product, we want to create a record in Django
            # to tie advertiser to the order
            if product_type == PRODUCT_TYPE_ADS_PACKAGE:

                # preprocessing
                ads_number, ads_create_duration, ads_display_name = get_attributes_from_product(product)

                start_date, end_date = calculate_start_and_end_date(ads_create_duration)

                ads_number, is_unlimited_ads = preprocess_ads_number(ads_number)

                # send graphql request to django
                create_ads_package(
                    name=product.name,
                    email=order.user_email,
                    order_id=order_id,
                    start_date=start_date,
                    end_date=end_date,
                    ads_number=ads_number,
                    is_unlimited_ads=is_unlimited_ads,
                    quantity=line.quantity,
                    display_name=ads_display_name,
                )

            elif product_type == PRODUCT_TYPE_ADD_ON:
                add_ons.append(
                    {
                        "quantity": line.quantity,
                        **get_attributes_from_add_on(product, line),
                    }
                )

        # send request to django to save add-ons
        if add_ons and len(add_ons) > 0:
            create_add_on(order_id, add_ons)

    except Order.DoesNotExist:
        print("Order is not found in CMS Integration - ", order_id)

    except Exception as e:
        print("Error in CMS Integration plugin order_fully_paid: ", e)


# parameter: order_id must be in relay global id format
def save_order_metadata(order_id, **kwargs):
    try:
        # convert relay global id to object id
        _, id = from_global_id(order_id)

        # make sure order exists
        order = Order.objects.get(id=id)
        order.metadata = {k: v or "-" for k, v in kwargs.items()}
        order.save()

    except Order.DoesNotExist:
        pass

    except Exception as e:
        print("Error in CMS Integration plugin save_order_metadata: ", e)
