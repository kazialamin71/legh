from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class appointment_payment(osv.osv):
    _name = "appointment.payment"




    _columns = {

        'cal_st_date': fields.date('Calculation Start Date'),
        'cal_end_date': fields.date('Calculation End Date'),
        'ref_doctors': fields.many2one('doctors.profile', 'Doctor Name'),
        'total_payable_amount': fields.float('Total Payable Amount'),
        'appointment_payment_line_ids':fields.one2many('appointment.payment.line','appointment_payment_line_ids','Payment Line')
    }

    @api.onchange('ref_doctors')
    def doctor_change(self):
        if self.ref_doctors:
            if self.cal_st_date == False or self.cal_end_date == False:
                raise osv.except_osv(_('Select'), _('Please select Start and End Date od Calculation'))

            st_date = self.cal_st_date
            end_date = self.cal_end_date
            commissioner_id = self.ref_doctors.id

            ## Get all Commission Configuration List
            # and appointment_payment.cal_st_date <= st_date and appointment_payment.cal_end_date >= end_date


            # import pdb
            # pdb.set_trace()
            query = "select appointment_booking.id,appointment_booking.patient_name,appointment_booking.patient_status,appointment_booking.amount from appointment_booking where appointment_booking.doctor_name=%s and appointment_booking.date >= %s and appointment_booking.date <= %s and payment_done=FALSE"
            self._cr.execute(query, (commissioner_id,st_date,end_date))
            all_data = self._cr.dictfetchall()
            # import pdb
            # pdb.set_trace()

            appointment_payment_line = list()


            total_amount = 0
            # total_billing_amount = 0
            # total_test_count = 0

            for bill_items in all_data:

               #
               # import pdb
               # pdb.set_trace()
               appointment_booking_id=bill_items.get("id")
               patient_name=bill_items.get("patient_name")
               patient_status=bill_items.get("patient_status")
               amount=bill_items.get("amount")
               total_amount = total_amount + bill_items.get("amount")

               appointment_payment_line.append({
                   'appointment_booking_id':appointment_booking_id,
                   'patient_name':patient_name,
                   'patient_status':patient_status,
                   'amount':amount

               })

               # import pdb
               # pdb.set_trace()


            self.appointment_payment_line_ids = appointment_payment_line
            self.total_payable_amount = total_amount

        return "xXxXxXxXxX"


    def appointment_pay(self, cr, uid, ids, context=None):
        cc_obj = self.browse(cr, uid, ids, context=context)
        for item in cc_obj.appointment_payment_line_ids:
            # import pdb
            # pdb.set_trace()

            item_id=item.appointment_booking_id
            query="update appointment_booking set payment_done=True where id=%s"
            cr.execute(query,([item_id]))
            cr.commit()
        return "XXXXX"



class appointment_payment_line(osv.osv):
        _name="appointment.payment.line"

        _columns = {
            'appointment_payment_line_ids':fields.many2one('appointment.payment','Admission Payment'),
            'appointment_booking_id':fields.char("Appointment ID"),
            'patient_name':fields.char("Patient Name"),
            'patient_status':fields.char("Patient Status"),
            'date':fields.date(string="Date"),
            'amount':fields.float('Amount'),


        }





