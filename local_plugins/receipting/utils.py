import os
import pytz
from decimal import Decimal
from datetime import datetime

from weasyprint import HTML
from django.conf import settings
from django.template.loader import get_template
from saleor.plugins.invoicing.utils import (
    MAX_PRODUCTS_WITH_TABLE,
    MAX_PRODUCTS_WITHOUT_TABLE,
    MAX_PRODUCTS_PER_PAGE,
)


def generate_invoice_number(order):
    # invoice format: <MY> + <calendar year> + <7 digit running number>
    # e.g.MY20210000001

    prefix = "MY"
    year = f"{order.created.year}"
    running_number = f"{order.id:07}"

    return prefix + year + running_number


def generate_receipt_number(order):
    # receipt format: <RMY> + <calendar year> + <7 digit running number>
    # e.g.RMY20210000001

    prefix = "RMY"
    year = f"{order.created.year}"
    running_number = f"{order.id:07}"

    return prefix + year + running_number


# receipt generation
# ----------------------


def chunk_products(products, product_limit):
    """Split products to list of chunks.

    Each chunk represents products per page, product_limit defines chunk size.
    """
    chunks = []
    for i in range(0, len(products), product_limit):
        limit = i + product_limit
        chunks.append(products[i:limit])
    return chunks


def get_product_limit_first_page(products):
    if len(products) < MAX_PRODUCTS_WITHOUT_TABLE:
        return MAX_PRODUCTS_WITH_TABLE

    return MAX_PRODUCTS_WITHOUT_TABLE


def format_price(price):
    return "MYR" + "{:.2f}".format(price)


# Saleor doesn't have receipt feature, hence use this function to generate a receipt
# pdf instead from an invoice object
# note: this is copied from the generate_invoice_pdf in saleor.saleor.plugins.invoicing.utils
def generate_receipt_pdf(invoice):

    # make sure this points to the correct html file
    receipt_html_path = "invoices/receipt.html"

    # these parts are exactly the same as the original function
    font_path = os.path.join(
        settings.PROJECT_ROOT, "templates", "invoices", "inter.ttf"
    )

    # get all products listed in the invoice, then break them into pages to be displayed
    # in the pdf
    all_products = invoice.order.lines.all()
    # product_limit_first_page = get_product_limit_first_page(all_products)
    # products_first_page = all_products[:product_limit_first_page]
    # rest_of_products = chunk_products(
    #     all_products[product_limit_first_page:], MAX_PRODUCTS_PER_PAGE
    # )
    products_first_page = all_products


    # get order object directly
    order = invoice.order

    # get meta data required
    tax_amount = Decimal(order.metadata.get("tax_amount", 0))
    agent_name = order.metadata.get("agent_name")
    payment_ref = order.metadata.get("payment_id")
    payment_method = order.metadata.get("payment_method")

    # calculate total discount
    subtotal_amount = order.undiscounted_total_gross_amount
    discounted_amount = order.total_gross_amount
    total_discount = subtotal_amount - discounted_amount
    total_amount = discounted_amount + tax_amount

    creation_date = datetime.now(tz=pytz.utc)

    # render html template with all the variables
    rendered_template = get_template(receipt_html_path).render(
        {
            "invoice": invoice,
            "creation_date": creation_date.strftime("%d %b %Y"),
            "agent_name": agent_name,
            "payment_ref": payment_ref,
            "payment_method": payment_method,
            "order": order,
            "tax_amount": format_price(tax_amount),
            "total_discount": format_price(total_discount),
            "total_amount": format_price(total_amount),
            "subtotal_amount": format_price(subtotal_amount),
            "font_path": f"file://{font_path}",
            "products_first_page": products_first_page,
            # "rest_of_products": rest_of_products,
        }
    )
    return HTML(string=rendered_template).write_pdf(), creation_date
