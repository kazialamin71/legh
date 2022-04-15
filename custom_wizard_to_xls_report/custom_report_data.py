from openerp import models, api
import datetime
from datetime import datetime


class sales_margin(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _report_xls_fields_custom(self):
        return [
            'name'
        ]

    # Change/Add Template entries
    @api.model
    def _report_xls_template(self):

        return {}
