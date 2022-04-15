from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class discount_category(osv.osv):
    _name = "discount.category"
    # _rec_name = 'patient_id'


    _columns = {

        'name': fields.char("Discount Type"),
        'parent':fields.many2one('discount.category','Parent Category'),
        'account_id':fields.many2one('account.account','Accounts')

    }