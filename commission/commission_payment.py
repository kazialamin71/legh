from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class commissionpayment(osv.osv):
    _name = "commission.payment"


    _columns = {

        'name': fields.char("CP No."),
        'doctor_id': fields.many2one('doctors.profile', 'Name'),
        'date':fields.date('Payment Date'),
        'cc_id': fields.many2one('commission', 'Commission'),
        'debit_id': fields.many2one('account.account', 'Debit Account'),
        'credit_id': fields.many2one('account.account', 'Credit Account'),
        'paid_amount': fields.float('Paid Amount'),
        'due_amount': fields.float('Due Amount'),
        'period_id': fields.many2one('account.period','Period'),
        'journal_id': fields.many2one('account.move','Journal'),
        'note': fields.text("Note"),

        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }
    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'


    def button_add_payment_action(self,cr,uid,ids,context=None):

        payment_obj=self.browse(cr,uid,ids,context=None)

        doc_name = payment_obj.doctor_id.name
        ref = payment_obj.cc_id.name

        ## Create Journal
        vals ={
                'name': '/',
                'period_id': payment_obj.period_id.id,
                'journal_id':5,
                'ref':ref,
                'date': date.today(),
                'line_id': [(0, 0, {
                        'name': doc_name,
                        'debit': payment_obj.paid_amount,
                        'account_id': payment_obj.debit_id.id,
                    }), (0, 0, {
                        'name': doc_name,
                        'credit': payment_obj.paid_amount,
                        'account_id': payment_obj.credit_id.id,
                    })]
            }

        journal_id = self.pool.get('account.move').create(cr, uid, vals, context=context)

        validate = self.pool.get('account.move').button_validate(cr, uid, [journal_id], context=context)

        payment_obj.journal_id = journal_id

        ## Ends Here


        ## Update Balance Here
        paid_amoount = payment_obj.paid_amount
        query = "update commission set state='paid',paid_amount=%s where id=%s"

        cr.execute(query, (paid_amoount, payment_obj.cc_id.id))
        cr.commit()


        ## Ends Update Balnce of CC Here


        ## Update Commission Calculation Date


        end_date = payment_obj.cc_id.cal_end_date
        doc_id = payment_obj.cc_id.ref_doctors.id
        query = "update doctors_profile set last_commission_calculation_date=%s where id=%s"

        cr.execute(query, (end_date, doc_id))
        cr.commit()

        ## Ends Here



        return payment_obj.id
