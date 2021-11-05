import pytz
import datetime
from saleor.plugins.base_plugin import BasePlugin
from .api import create_ads_package


class DjangoCMSPlugin(BasePlugin):
    PLUGIN_ID = "local_plugins.cms.plugin"
    PLUGIN_NAME = "Django CMS Integration"
    DEFAULT_ACTIVE = True

    def order_fully_paid(self, order, previous_value):
        try:
            print("Order is fully paid: ", order)

            order_lines = order.lines.all()

            # go through each product in the order
            for line in order_lines:

                # retrieve the actual product object from db
                product = line.variant.product
                type = product.product_type

                # for Ads Package product, we want to create a record in Django
                # to tie advertiser to the order
                if type.name == "Ads Package":

                    ads_number, ads_create_duration = get_attributes_from_product(
                        product
                    )

                    start_date, end_date = calculate_start_and_end_date(
                        ads_create_duration
                    )

                    # preprocessing before sending the graphql
                    # ------------------

                    # check if ads number is unlimited
                    if ads_number == "Unlimited":
                        ads_number = None
                        is_unlimited_ads = True
                    else:
                        ads_number = int(ads_number)
                        is_unlimited_ads = False

                    create_ads_package(
                        email=order.user_email,
                        order_id=order.id,
                        start_date=start_date,
                        end_date=end_date,
                        ads_number=ads_number,
                        is_unlimited_ads=is_unlimited_ads,
                        sales_amount=float(order.total_gross_amount),
                    )

        except Exception as e:
            print("Error in CMS Integration plugin order_fully_paid: ", e)
            pass

        # send mutation here to Django


# helper functions
# ---------------------

# this is a function meant for getting 'ads_number' & 'ads_create_duration'
# attribute values from a product only
def get_attributes_from_product(product):
    ads_number = None
    ads_create_duration = None

    # get values for number of ads & ads-create duration from the
    # product attributes
    for attr in product.attributes.all():

        # get attribute name
        name = attr.assignment.attribute.name

        # note we allow 1 value for an attribute, hence we always
        # get the first one
        value = attr.values.all()[0].name

        if name == "Number of Ads":
            ads_number = value

        if name == "Ads-create Duration":
            ads_create_duration = value

    # return all values retrieved
    return ads_number, ads_create_duration


# this is a function meant for calculating start & end date for ads package only
def calculate_start_and_end_date(ads_create_duration):
    # important: must follow utc time
    start_date = datetime.datetime.now(pytz.utc)
    end_date = start_date
    duration = 0

    # convert ads_create_duration in string format to days unit
    if ads_create_duration == "1-Week":
        duration = 7
    elif ads_create_duration == "1-Month":
        duration = 30

    # calculate end date
    end_date += datetime.timedelta(days=duration)

    return start_date.isoformat(), end_date.isoformat()
