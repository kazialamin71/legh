from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class bill_register(osv.osv):
    _name = "opd.ticket.entry"
    _order = 'id desc'



    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name':fields.char("Name"),
        'department':fields.many2one("diagnosis.department","Department"),
        'fee': fields.float("Fee"),
        'accounts_id':fields.many2one('account.account',"Account ID",required=True)
    }

