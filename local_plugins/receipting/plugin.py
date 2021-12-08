from saleor.plugins.base_plugin import BasePlugin
from saleor.invoice.models import Invoice
from django.utils.text import slugify
from django.core.files.base import ContentFile
from saleor.core import JobStatus
from uuid import uuid4
from .utils import (
    generate_invoice_number,
    generate_receipt_number,
    generate_receipt_pdf,
)


class ReceiptingPlugin(BasePlugin):
    PLUGIN_ID = "local_plugins.receipting"
    PLUGIN_NAME = "Receipting"
    DEFAULT_ACTIVE = True
    PLUGIN_DESCRIPTION = "Custom plugin that handles receipt creation."
    CONFIGURATION_PER_CHANNEL = False

    def invoice_request(self, order, invoice, number, previous_value):
        # update invoice no to follow the format requested by the client
        invoice_number = generate_invoice_number(order)
        invoice.update_invoice(number=invoice_number)
        invoice.save()

        # receipt generation
        # -------------------
        # create receipt as an invoice object and generate the receipt pdf
        receipt = Invoice(order=order, message="receipt")

        # create receipt no using format requested by the client
        receipt_number = generate_receipt_number(order)
        receipt.update_invoice(number=receipt_number)

        # generate pdf and save into db
        receipt_pdf, creation_date = generate_receipt_pdf(receipt)
        receipt.created = creation_date
        receipt.invoice_file.save(
            f"receipt-{slugify(receipt_number)}-order-{order.id}-{uuid4()}.pdf",
            ContentFile(receipt_pdf),
        )

        receipt.status = JobStatus.SUCCESS
        receipt.save(
            update_fields=[
                "number",
                "created",
                "invoice_file",
                "status",
                "updated_at",
                "message",
            ]
        )

        # # note: must return the invoice object
        return invoice
