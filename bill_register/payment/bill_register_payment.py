from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime
from datetime import date, time, timedelta, datetime




class bill_register_payment(osv.osv):
    _name = 'bill.register.payment'
    _description = "bill register Payment"


    def button_add_payment_action(self,cr,uid,ids,context=None):
        payment_obj=self.browse(cr,uid,ids,context=None)
        bill_id=payment_obj.bill_id.id
        bill_register_id=payment_obj.bill_id.name
        eve_mee_obj = self.pool.get('bill.register.payment.line')
        pay_date=payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.payment_type.name
        pay_card=payment_obj.account_number
        current_due =payment_obj.bill_id.due
        current_paid =payment_obj.bill_id.paid
        money_receipt_id =payment_obj.money_receipt_id.id

        updated_amount = current_due-pay_amount
        updated_paid = current_paid+pay_amount
        if updated_amount <0:
            updated_amount=0

        service_dict={'date': pay_date,'amount':pay_amount,'type': pay_type,'card_no':pay_card ,'bill_register_payment_line_id': bill_id,'money_receipt_id':money_receipt_id}

        service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)


        cr.execute("update bill_register set due=%s,paid=%s where id=%s", (updated_amount,updated_paid,bill_id))
        cr.commit()
        # ###journal_entry
        journal_object = self.pool.get("bill.journal.relation")
        line_ids = []

        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        period_id = periods and periods[0] or False
        # if payment method is cash
        # import pdb
        # pdb.set_trace()

        if current_paid > 0 and payment_obj.payment_type.name=='Cash':

            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'tax_code_id': False,
                'tax_amount': 0,
                'name': bill_register_id,
                'currency_id': False,
                'credit': 0,
                'date_maturity': False,
                'account_id': 6,  ### Cash ID
                'debit': pay_amount,
                'amount_currency': 0,
                'partner_id': False,
            }))
            if context is None:
                context = {}

            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'tax_code_id': False,
                'tax_amount': 0,
                'name': bill_register_id,
                'currency_id': False,
                'credit': pay_amount,
                'date_maturity': False,
                'account_id': 771,  ### Accounts Receivable ID
                'debit': 0,
                'amount_currency': 0,
                'partner_id': False,
            }))
            # end of condition
            # Payment method is card

        if current_paid > 0 and payment_obj.payment_type.name=='Visa Card':
            other_method_pay = payment_obj.to_be_paid
            service_charge=payment_obj.service_charge

            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'tax_code_id': False,
                'tax_amount': 0,
                'name': bill_register_id,
                'currency_id': False,
                'credit': 0,
                'date_maturity': False,
                'account_id':payment_obj.payment_type.account.id ,  ### Cash ID
                'debit': other_method_pay,
                'amount_currency': 0,
                'partner_id': False,
            }))
            if context is None:
                context = {}

            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'tax_code_id': False,
                'tax_amount': 0,
                'name': bill_register_id,
                'currency_id': False,
                'credit': pay_amount,
                'date_maturity': False,
                'account_id': 771,  ### Accounts Receivable ID
                'debit': 0,
                'amount_currency': 0,
                'partner_id': False,
            }))

            if service_charge>0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': bill_register_id,
                    'currency_id': False,
                    'credit': service_charge,
                    'date_maturity': False,
                    'account_id': payment_obj.payment_type.service_charge_account.id,  ### Accounts Receivable ID
                    'debit': 0,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

        jv_entry = self.pool.get('account.move')

        j_vals = {'name': '/',
                  'journal_id': 2,  ## Cash Journal
                  'date': fields.date.today(),
                  'period_id': period_id,
                  'ref': bill_register_id,
                  'line_id': line_ids

                  }

        # import pdb
        # pdb.set_trace()
        saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)

        if saved_jv_id > 0:
            if saved_jv_id > 0:
                journal_id = saved_jv_id
                try:
                    jv_entry.button_validate(cr,uid, [saved_jv_id], context)
                    journal_dict = {'journal_id': journal_id, 'bill_journal_relation_id': bill_id}
                    journal_object.create(cr, uid, vals=journal_dict, context=context)
                except:
                    import pdb
                    pdb.set_trace()
        ###end journal

        return service_id

    def _default_payment_type(self):
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {
        'name':fields.char("Cash Collection ID", readonly=True),
        'bill_id': fields.many2one('bill.register', 'Bill ID', readoly=True),
        'date': fields.date(string='Your string', default=datetime.today()),
        'amount': fields.float('Receive Amount', required=True),
        'payment_type': fields.many2one('payment.type','Payment Type',default=_default_payment_type),
        'service_charge': fields.float("Service Charge"),
        'to_be_paid': fields.float("To be Paid"),
        'account_number':fields.char('Account No.'),
        'money_receipt_id': fields.many2one('legh.money.receipt', 'Money Receipt ID'),
    }

    def create(self,cr,uid,vals,context):
        storedpayment = super(bill_register_payment, self).create(cr, uid, vals, context)  # return ID int object

        if storedpayment is not None:
            name_text = 'CC-100' + str(storedpayment)
            cr.execute('update bill_register_payment set name=%s where id=%s', (name_text, storedpayment))
            cr.commit()
        value={}
        value['date']=vals['date']
        value['bill_id']=vals['bill_id']
        value['amount']=vals['amount']
        value['type']=vals['payment_type']
        value['p_type'] = 'due_payment'

        # value['user_id']=vals['user_id']
        stored_obj = self.pool.get("bill.register").browse(cr, uid, vals['bill_id'], context=None)
        diagonostic_bill = stored_obj.diagonostic_bill
        value['diagonostic_bill'] = diagonostic_bill

        mr_object=self.pool.get("legh.money.receipt")
        mr_id=mr_object.create(cr, uid, value, context=context)
        if mr_id is not None:
            mr_name='MR#' +str(mr_id)
            cr.execute('update legh_money_receipt set name=%s where id=%s',(mr_name,mr_id))
            cr.execute('update bill_register_payment set money_receipt_id=%s where id=%s',(mr_id,storedpayment))
            cr.commit()

        #confirm on paid
        return storedpayment

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active==True:
            interest=self.payment_type.service_charge
            if interest>0:
                service_charge=(self.amount*interest)/100
                self.service_charge=service_charge
                self.to_be_paid=self.amount+service_charge
            else:
                self.to_be_paid=self.amount
                self.service_charge=0
        return "X"
