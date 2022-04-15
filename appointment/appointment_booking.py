from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class appointment_booking(osv.osv):
    _name = "appointment.booking"




    _columns = {

        'name': fields.char("Appointment"),
        'patient_name':fields.char('Patient Name',required=True),
        'age':fields.char('Age',required=True),
        'sex':fields.char('Sex'),
        'phone': fields.char('Mobile No.'),
        'address': fields.char('Address'),
        'doctor_name': fields.many2one('doctors.profile','Doctor Name'),
        'time':fields.char('Time'),
        'date':fields.date('Date'),
        'status': fields.selection([('pending', 'Pending'), ('reached', 'Reached'), ('paid', 'Paid')], string='Status',
                                   default='pending'),
        'patient_status': fields.selection([('new', 'New Patient'), ('review', 'Review')],string="Patient Status"),
        'amount': fields.float('amount'),
        'payment_done': fields.boolean("Payment", default=False)
    }

    def reached_appointment(self, cr, uid, ids, context=None):
        ## Bill Status Will Change

        cr.execute("update appointment_booking set status='reached' where id=%s", (ids))
        cr.commit()
        return True

    def done_appointment(self, cr, uid, ids, context=None):
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legh',
                                                                             'appointment_paid_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)

        # total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'appointment.paid',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'appointment_id': ids[0],
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))