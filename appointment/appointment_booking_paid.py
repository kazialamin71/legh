from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class appointment_booking_paid(osv.osv):
    _name = "appointment.paid"




    _columns = {

        'patient_status': fields.selection([('new', 'New Patient'), ('review', 'Review')], string="Patient Status"),
        'amount': fields.float('amount')
        # 'nid':fields.integer("NID")
    }

    def button_add_payment_action(self,cr,uid,ids,context=None):
        payment_object = self.browse(cr, uid, ids, context=None)
        patient_status=payment_object.patient_status
        amount=payment_object.amount
        appointment_id=context.get("appointment_id")
        # import pdb
        # pdb.set_trace()

        cr.execute('update appointment_booking set patient_status=%s,amount=%s where id=%s',
                   (patient_status,amount,appointment_id))
        cr.commit()

        return True