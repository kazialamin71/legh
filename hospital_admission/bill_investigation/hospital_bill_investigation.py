from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class patient_guarantor(osv.osv):
    _name = "bill.investigation"
    _rec_name = "bill_id"

    _columns = {
        'bill_id': fields.char("Bill ID:"),
        'patient_name': fields.char("Patient Name"),
        'department': fields.char("Department"),
        'mobile': fields.char("Mobile"),
        'item_name': fields.char("Item Name"),
        'item_qty': fields.char('Item Quantity'),
        'unit_price': fields.char('Unit Price'),
        'price': fields.char('Price'),
        'discount': fields.char('Discount'),
        'total_price': fields.char("Total Price"),
    }