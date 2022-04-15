from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time


class sample_type(osv.osv):
    _name = "sample.type"

    _columns = {

        'name': fields.char("Sample Type",required=True),


    }
