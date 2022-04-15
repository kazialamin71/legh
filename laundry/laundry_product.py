from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class laundry(osv.osv):
    _name = "laundry.product"




    _columns = {

        'name': fields.char("Name",required=True),
        'color':fields.char('Color',required=True),
        'quantity':fields.integer('Quantity',required=True),
        'type': fields.selection([('general', 'General Purpose Linen'), ('patient', 'Patient Linen'),('ward', 'Ward Linen')],string="Type"),
        'others': fields.char("Others")
        # 'nid':fields.integer("NID")

    }