from openerp import api
from openerp.osv import osv, fields

class pos_order(osv.osv):
    _inherit = 'pos.order'

    _columns = {
        'general_admission_id': fields.many2one('hospital.admission', 'General Admission ID'),
        'patient_name': fields.many2one('patient.info', 'Patient Name'),
    }

    @api.onchange('general_admission_id')
    def onchange_general_admission_pharmacy(self):
        general_admission_obj = self.env['hospital.admission'].search([('id', '=', self.general_admission_id.id)])
        self.patient_name = general_admission_obj.patient_name
