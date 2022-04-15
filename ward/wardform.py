from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class ward(osv.osv):
    _name = "ward.managment"




    _columns = {

        'wname': fields.char("Ward Name",required=True),
        'bed': fields.char("Bed No", required=True),
        'name': fields.char("Patient Name", required=True),
        'pid': fields.char("Patient ID", required=True),
        'Date': fields.datetime("Recived Date", required=True),
        'precived': fields.char("Recived By", required=True),


    }



# class purchase_order_line(osv.osv):
#     _inherit='purchase.order.line'
#
#     def _last_purchase_date(self, cr, uid, ids, field_name, arg, context=None):
#         import pdb
#         pdb.set_trace()
#
#
#         Percentance_calculation[record.id] = date.today()
#
#         return Percentance_calculation
#
#     def _last_purchase_qty(self,cr, uid, ids, field_name, arg, context=None):
#         return True
#
#     _columns = {
#         'last_purchase_date': fields.date(compute=_last_purchase_date, string='Last Purchase Date'),
#         'last_purchase_qty': fields.function(_last_purchase_qty, string='Last Purchase Date')
#     }
#
