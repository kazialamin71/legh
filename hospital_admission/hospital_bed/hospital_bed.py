from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class hospital_bed(osv.osv):
    _name = "hospital.bed"

    _columns = {
        'name': fields.char("Bed Number"),
        'bed_qty': fields.char('Bed Quantity'),
        'perday_charge': fields.float('Per Day Charge'),
        'total_amount': fields.float("Total Amount"),
        'ward_name': fields.char("Ward Name"),

    }
