from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class patient_guarantor(osv.osv):
    _name = "hospital.patient.guarantor"




    _columns = {
        'name': fields.char("Guarantor Name"),
        'address': fields.char('Address'),
        'relationship': fields.char('Relationship'),
        'contact': fields.char("Contact"),
        'email': fields.char("Email"),
        'admission_id': fields.many2one('hospital.admission', 'parent'),
    }