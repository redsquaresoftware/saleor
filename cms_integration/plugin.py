from saleor.plugins.base_plugin import BasePlugin


class CMSIntegrationPlugin(BasePlugin):
    PLUGIN_ID = "cms_integration.plugin"
    PLUGIN_NAME = "CMS Integration"
    DEFAULT_ACTIVE = True

    def order_created(self, order, previous_value):
        print("IN CMS INTEGRATION PLUGIN - SELF: ", self)
        print("IN CMS INTEGRATION PLUGIN - Order: ", order)
        print("IN CMS INTEGRATION PLUGIN - Previous Value: ", previous_value)
