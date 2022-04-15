from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import SUPERUSER_ID, api

class payment_type(osv.osv):
    _name = "payment.type"

    _columns = {

        'name': fields.char("Name",required=True),
        'account': fields.many2one('account.account', string='Account',required=True),
        'service_charge_account': fields.many2one('account.account', string='Service Charge Account'),
        'service_charge': fields.float("Service Charge", required=True),
        'service_charge_flat': fields.char("Service Charge(Flat)"),
        'active':fields.boolean("Active")
    }
