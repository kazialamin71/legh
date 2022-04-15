from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class patient_guarantor(osv.osv):
    _name = "patient.guarantor"




    _columns = {

        'name': fields.char("Guarantor Name"),
        'contact': fields.char("Contact"),
        'admission_id':fields.many2one('leih.admission','parent')

    }