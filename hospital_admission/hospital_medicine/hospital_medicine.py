from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class Hospital_Medicine(osv.osv):
    _name = "hospital.medicine"
    _rec_name = "product_name"

    _columns = {
        'product_name': fields.char("Medicine Name"),
        'product_qty': fields.char('Product Quantity'),
        'unit_price': fields.char('Unit Price'),
        'total_price': fields.char("Total Price"),
    }