from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time, timedelta, datetime

class discount(osv.osv):
    _name = "discount"
    _order = 'id desc'
    # _rec_name = 'patient_id'


    _columns = {

        'name': fields.char("Discount Number"),
        'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
        'admission_id':fields.many2one("leih.admission","Admission ID"),
        'bill_no': fields.many2one('bill.register','Bill No'),
        'patient_name': fields.char("Patient Name",required=True),
        'mobile': fields.char("Mobile Number", required=True),
        'total_discount':fields.float('Total Discount'),
        'amount': fields.integer("Amount"),
        'state': fields.selection([
            ('pending', 'Pending'),
            ('approve', 'Approved'),
            ('cancel', 'Cancelled')],'State',default='pending',readonly=True),
        'discount_line_id': fields.one2many("discount.line",'discount_id','Discount Line',required=True),
    }

    def approve_discount(self,cr,uid,ids,context=None):
        discount_object = self.browse(cr, uid, ids, context=None)
        if discount_object.state=='approve':
            raise osv.except_osv(_('Warning!'),
                                 _('Discount is already confirmed!'))

        else:
            bill_id=discount_object.bill_no.id
            bill_name=discount_object.bill_no
            admission_id=discount_object.admission_id.id
            admission_name=discount_object.admission_id
            total_discount=discount_object.total_discount

            # confirm button code
            if bill_id != False:
                # fetching data from bill_register
                query = "select grand_total,paid,due,state from bill_register where id=%s"
                cr.execute(query, ([bill_id]))
                all_data = cr.dictfetchall()

                if all_data[0]['state']!='confirmed':
                    raise osv.except_osv(_('Error!'),
                                         _('The bill is not in confirmed state yet!'))

                for item in all_data:
                    grand_total = item.get('grand_total')
                    paid_amount = item.get('paid')
                    due_amount = item.get('due')
                if due_amount < total_discount:
                    raise osv.except_osv(_('Warning!'),
                                         _('Not permissed to make discount more than due!'))
                elif due_amount >= total_discount:
                    grand_total = grand_total - total_discount
                    due_amount = due_amount - total_discount

                cr.execute('update bill_register set other_discount=%s,grand_total=%s,due=%s where id=%s',
                           (total_discount, grand_total, due_amount, bill_id))
                cr.commit()

                # journal entry for approve discount
                line_ids = []

                if context is None: context = {}
                if context.get('period_id', False):
                    return context.get('period_id')
                periods = self.pool.get('account.period').find(cr, uid, context=context)
                period_id = periods and periods[0] or False


                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': discount_object.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': discount_object.discount_line_id.accounts.id,  ### Cash ID
                    'debit': total_discount,
                    'amount_currency': 0,
                    'partner_id': False,
                }))
                if context is None:
                    context = {}

                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': discount_object.name,
                    'currency_id': False,
                    'credit': total_discount,
                    'date_maturity': False,
                    'account_id': 195,  ### Accounts Receivable ID
                    'debit': 0,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

                jv_entry = self.pool.get('account.move')

                j_vals = {'name': '/',
                          'journal_id': 6,  ## Cash Journal
                          'date': fields.date.today(),
                          'period_id': period_id,
                          'ref': discount_object.bill_no,
                          'line_id': line_ids

                          }

                # import pdb
                # pdb.set_trace()
                saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)

                if saved_jv_id > 0:
                    if saved_jv_id > 0:
                        journal_id = saved_jv_id
                        try:
                            jv_entry.button_validate(cr, uid, [saved_jv_id], context)
                        except:
                            import pdb
                            pdb.set_trace()

            elif admission_id != False:
                query = "select grand_total,paid,due from leih_admission where id=%s"
                cr.execute(query, ([admission_id]))
                all_data = cr.dictfetchall()
                grand_total = 0
                paid_amount = 0
                due_amount = 0
                for item in all_data:
                    grand_total = item.get('grand_total')
                    paid_amount = item.get('paid')
                    due_amount = item.get('due')

                if due_amount < total_discount:
                    raise osv.except_osv(_('Warning!'),
                                         _('Not permissed to make discount more than due!'))
                elif due_amount >= total_discount:
                    grand_total = grand_total - total_discount
                    due_amount = due_amount - total_discount
                cr.execute('update leih_admission set other_discount=%s,grand_total=%s,due=%s where id=%s',
                           (total_discount, grand_total, due_amount, admission_id))
                cr.commit()

                # journal entry will be here
                # journal entry for approve discount
                line_ids = []

                if context is None: context = {}
                if context.get('period_id', False):
                    return context.get('period_id')
                periods = self.pool.get('account.period').find(cr, uid, context=context)
                period_id = periods and periods[0] or False

                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': discount_object.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': discount_object.discount_line_id.accounts.id,  ### Cash ID
                    'debit': total_discount,
                    'amount_currency': 0,
                    'partner_id': False,
                }))
                if context is None:
                    context = {}

                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': discount_object.name,
                    'currency_id': False,
                    'credit': total_discount,
                    'date_maturity': False,
                    'account_id': 195,  ### Accounts Receivable ID
                    'debit': 0,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

                jv_entry = self.pool.get('account.move')

                j_vals = {'name': '/',
                          'journal_id': 6,  ## Cash Journal
                          'date': fields.date.today(),
                          'period_id': period_id,
                          'ref': discount_object.bill_no,
                          'line_id': line_ids

                          }

                # import pdb
                # pdb.set_trace()
                saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)

                if saved_jv_id > 0:
                    if saved_jv_id > 0:
                        journal_id = saved_jv_id
                        try:
                            jv_entry.button_validate(cr, uid, [saved_jv_id], context)
                        except:
                            import pdb
                            pdb.set_trace()

            # end confirm button code


            if ids is not None:
                cr.execute("update discount set state='approve' where id=%s", (ids))
                cr.commit()
            return True
        def cancel_discount(self,cr,uid,ids,context=None):
            if ids is not None:
                cr.execute("update discount set state='cancel' where id=%s", (ids))
                cr.commit()
        return True


    @api.onchange('discount_line_id')
    def onchange_discount_item(self):
        total_amount=self.amount
        listfixed=[]
        listpercent=[]

        for item in self.discount_line_id:
            fixed_amount=item.fixed_amount
            percent_amount=item.percent_amount
            listfixed.append(fixed_amount)
            listpercent.append(percent_amount)
        total_percent = sum(listpercent)
        total_fixed = sum(listfixed)
        percent_discounted_amount = (total_amount * total_percent) / 100
        total_discount=total_fixed+percent_discounted_amount
        self.total_discount=total_discount
        return "X"


    def onchange_bill(self,cr,uid,ids,bill_no,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('bill.register').browse(cr, uid,bill_no, context=None)
        patient_name=dep_object.patient_name.name
        mobile=dep_object.patient_name.mobile
        amount=dep_object.due
        abc = {'patient_name': patient_name,'mobile':mobile,'amount':amount}
        tests['value'] = abc
        return tests
    def onchange_admission(self,cr,uid,ids,admission_id,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.admission').browse(cr, uid,admission_id, context=None)
        patient_name=dep_object.patient_name.name
        mobile=dep_object.patient_name.mobile
        amount=dep_object.grand_total
        abc = {'patient_name': patient_name,'mobile':mobile,'amount':amount}
        tests['value'] = abc
        return tests

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(discount, self).create(cr, uid, vals, context)  # return ID int object

        if stored is not None:
            name_text = 'Dis-10' + str(stored)
            cr.execute('update discount set name=%s where id=%s', (name_text, stored))
            cr.commit()
        return stored

class discount_line(osv.osv):
    _name = "discount.line"
    # _rec_name = 'patient_id'


    _columns = {

        'category':fields.many2one('discount.category', 'Discount Category'),
        # 'category':fields.char('Category'),
        'ref': fields.char("Reference"),
        'accounts':fields.many2one("account.account","Account Name"),
        'fixed_amount': fields.integer("Amount(fixed)"),
        'percent_amount': fields.integer("Amount(%)"),
        'discount_id': fields.many2one("discount","discount Id")
    }

    def onchange_category(self, cr, uid, ids, name, context=None):
        tests = {'values': {}}
        # code for delivery date

        dep_object = self.pool.get('discount.category').browse(cr, uid, name, context=None)
        account_id=dep_object.account_id
        if account_id.id is False:
            account_id=self.pool.get('account.account').browse(cr, uid, 7798, context=None)

        abc = {'accounts': account_id}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    # def onchange_type(self,cr,uid,ids,type,context=None):
    #     values={}
    #     discount_type_obj=self.pool.get('discount.core.type').browse(cr,uid,type,context=None)
    #     category_id=discount_type_obj.category_id.name
    #     amount=discount_type_obj.discount_amount
    #     accounts=discount_type_obj.account_id
    #     new_dict={'category':category_id,'percent_amount':amount,'accounts':accounts}
    #     values['value']=new_dict
    #     return values
