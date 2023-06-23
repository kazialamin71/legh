from openerp import api
from openerp.exceptions import ValidationError
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import date, time, timedelta, datetime
from openerp.tools.amount_to_text_en import amount_to_text



class bill_register(osv.osv):
    _inherit = 'bill.register'

    _columns = {
        'general_admission_id': fields.many2one('hospital.admission','General Admission ID'),
        'is_applied_to_admission':fields.boolean('Is applied')
    }

    @api.onchange('general_admission_id')
    def onchange_general_admission(self):
        general_admission_obj = self.env['hospital.admission'].search([('id', '=', self.general_admission_id.id)])
        self.patient_name=general_admission_obj.patient_name