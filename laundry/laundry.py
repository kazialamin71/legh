from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class laundry(osv.osv):
    _name = "laundry.laundry"




    _columns = {

        'name': fields.char("Name",required=True),
        'address':fields.char('Address',required=True),


    }