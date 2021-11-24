import pytz
import datetime
from .constants import *


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

        # get attribute name in uppercase
        name = attr.assignment.attribute.name.upper()

        # note we allow 1 value for an attribute, hence we always
        # get the first one
        value = attr.values.all()[0].name

        if name == ATTRIBUTE_NUMBER_OF_ADS:
            ads_number = value

        if name == ATTRIBUTE_DURATION:
            ads_create_duration = value

    # return all values retrieved
    return ads_number, ads_create_duration


# this is a function meant for calculating start & end date for ads package only
def calculate_start_and_end_date(ads_create_duration):
    # important: must follow utc time
    start_date = datetime.datetime.now(pytz.utc)
    end_date = start_date
    duration_in_days = 0

    # standarize string comparison
    ads_create_duration = ads_create_duration.upper()

    # convert ads_create_duration in string format to days unit
    if ads_create_duration == DURATION_1_DAY:
        duration_in_days = 1
    elif ads_create_duration == DURATION_1_WEEK:
        duration_in_days = 7
    elif ads_create_duration == DURATION_1_MONTH:
        duration_in_days = 30
    elif ads_create_duration == DURATION_6_MONTH:
        duration_in_days = 180
    elif ads_create_duration == DURATION_1_YEAR:
        duration_in_days = 365

    # calculate end date
    end_date += datetime.timedelta(days=duration_in_days)

    return start_date.isoformat(), end_date.isoformat()


# this is a function meant for processing ads_number and is_unlimited_ads
def preprocess_ads_number(ads_number):
    # check if ads number is unlimited
    if ads_number.upper() == NUMBER_OF_ADS_UNLIMITED:
        ads_number = None
        is_unlimited_ads = True
    else:
        ads_number = int(ads_number)
        is_unlimited_ads = False

    return ads_number, is_unlimited_ads


def get_attributes_from_add_on(product, line):
    product_name = product.name.upper()

    # add on must have the following attributes:
    # 1. only one product attribute with one value only
    # 2. only one variant attribute with one value only
    product_attr = product.attributes.all().first()
    product_attr_value = product_attr.values.all().first().name

    variant_attr = line.variant.attributes.all().first()
    variant_attr_value = variant_attr.values.all().first().name

    # default attribute values
    add_on_type = None
    is_mywheels = False
    is_cp_regional = False
    region = None
    add_on_duration = product_attr_value.upper()

    if product_name == ADD_ON_PREMIUM:
        add_on_type = DJANGO_ENUM_ADD_ON_PREMIUM

    elif product_name == ADD_ON_MYWHEELS_FEATURE:
        add_on_type = DJANGO_ENUM_ADD_ON_FEATURED
        is_mywheels = True

    elif product_name == ADD_ON_MYWHEELS_FB_POST:
        add_on_type = DJANGO_ENUM_ADD_ON_FB_POST
        is_mywheels = True

    elif product_name == ADD_ON_MYWHEELS_FB_PIN:
        add_on_type = DJANGO_ENUM_ADD_ON_FB_PIN
        is_mywheels = True

    elif product_name == ADD_ON_CP_REGIONAL_FEATURE:
        add_on_type = DJANGO_ENUM_ADD_ON_FEATURED
        is_cp_regional = True
        region = variant_attr_value

    elif product_name == ADD_ON_CP_REGIONAL_FB:
        add_on_type = DJANGO_ENUM_ADD_ON_FB_POST
        is_cp_regional = True
        region = variant_attr_value

    elif product_name == ADD_ON_CP_REGIONAL_FB_PIN:
        add_on_type = DJANGO_ENUM_ADD_ON_FB_PIN
        is_cp_regional = True
        region = variant_attr_value

    # convert add-on duration to django enum
    if add_on_duration == ADD_ON_DURATION_3_DAY:
        add_on_duration = DJANGO_ENUM_ADD_ON_THREE_DAY

    elif add_on_duration == ADD_ON_DURATION_UNLIMITED:
        add_on_duration = DJANGO_ENUM_ADD_ON_UNLIMITED

    return {
        "add_on_type": add_on_type,
        "is_mywheels": is_mywheels,
        "is_cp_regional": is_cp_regional,
        "region": region,
        "add_on_duration": add_on_duration,
    }
