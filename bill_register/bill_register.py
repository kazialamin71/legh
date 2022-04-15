from openerp import api
from openerp.exceptions import ValidationError
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import date, time, timedelta, datetime
from openerp.tools.amount_to_text_en import amount_to_text




class bill_register(osv.osv):
    _name = "bill.register"
    _order = 'id desc'
    # pdf=PDF()

    # pdf.lines()
    # pdf.titles()

    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("bill.register").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.bill_register_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum=item+sum


                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum

        return Percentance_calculation
    def _delivery_dates(self, cr, uid, ids, field_name, arg, context=None):
        delivery_date={}
        test_delivery_date=[]
        max_day=0
        for items in self.pool.get("bill.register").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.bill_register_line_id:
                for test in amount.name:

                    test_delivery_date.append(test.required_time)

        if len(test_delivery_date):
            max_day=max(test_delivery_date)
        #
        # import pdb
        # pdb.set_trace()

            # for item in total_list:
            #     sum=item+sum
        for record in self.browse(cr,uid,ids,context=context):
            delivery_date[record.id]=date.today()+timedelta(days=max_day)

        # import pdb
        # pdb.set_trace()
        return delivery_date

    def _default_payment_type(self):
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name':fields.char("Name"),
        'mobile': fields.char(string="Mobile",store=False),
        'patient_id': fields.char(related='patient_name.patient_id',string="Patient Id",readonly=True),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address",store=False),
        'age': fields.char("Age",store=False),
        'sex':fields.char("Sex",store=False),
        'referral':fields.char("Referral"),
        'diagonostic_bill':fields.boolean("Diagonstic Bill"),
        'ref_doctors': fields.many2one('doctors.profile','Reffered by'),
        'delivery_date': fields.function(_delivery_dates,string="Delivery Date",type='date',store=True),
        'bill_register_line_id': fields.one2many('bill.register.line', 'bill_register_id', 'Item Entry',required=True),
        'bill_register_payment_line_id': fields.one2many("bill.register.payment.line", "bill_register_payment_line_id","Bill Register Payment"),
        'bill_journal_relation_id': fields.one2many("bill.journal.relation", "bill_journal_relation_id","Journal"),
        # 'footer_connection': fields.one2many('leih.footer', 'relation', 'Parameters', required=True),
        # 'relation': fields.many2one("leih.investigation"),
        # 'total': fields.float(_totalpayable,string="Total",type='float',store=True),
        'total_without_discount': fields.float(string="Total without discount"),
        'total': fields.float(string="Total"),
        'doctors_discounts': fields.float("Doctor Discount(%)"),
        'after_discount': fields.float("Discount Amount"),
        'other_discount': fields.float("Other Discount"),
        'grand_total': fields.float("Grand Total"),
        'paid': fields.float(string="Paid",required=True),
        'type': fields.selection([('cash', 'Cash'),('bank', 'Bank')], 'Payment Type'),
        'card_no': fields.char('Card No.'),
        'bank_name': fields.char('Bank Name'),
        'due': fields.float("Due"),
        'date':fields.datetime("Date", readonly=True,default=lambda self: fields.datetime.now()),
        'user_id': fields.many2one('res.users', 'Assigned to', select=True, track_visibility='onchange'),
        'state': fields.selection(
            [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True),
        'old_journal': fields.boolean("Old Journal"),
        # new attributes for payment type
        'payment_type': fields.many2one("payment.type", "Payment Type", default=_default_payment_type),
        'service_charge': fields.float("Service Charge"),
        'to_be_paid': fields.float("To be Paid"),
        'account_number': fields.char("Account Number")

    }
    _defaults = {
        'diagonostic_bill': False,
        'user_id': lambda obj, cr, uid, context: uid,
    }

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active==True:
            interest=self.payment_type.service_charge
            if interest>0:
                service_charge=(self.paid*interest)/100
                self.service_charge=service_charge
                self.to_be_paid=self.paid+service_charge
            else:
                self.to_be_paid=self.paid
                self.service_charge=0
        return "X"

    @api.multi
    def amount_to_text(self, amount, currency='Bdt'):
        text = amount_to_text(amount, currency)
        new_text = text.replace("euro", "Taka")
        # initializing sub string
        sub_str = "Taka"
        final_text = new_text[:new_text.index(sub_str) + len(sub_str)]


        # final_text = new_text.replace("Cent", "Paisa")
        return final_text

    @api.multi
    def advance_paid(self,name):
        bill_obj = self.env['bill.register'].search([('name', '=', name)])
        if bill_obj.state!='confirmed':
            raise osv.except_osv(_('Warning!'),
                                 _('Confirm your bill first.'))
        elif bill_obj.state=='confirmed':
            mr = self.env['leih.money.receipt'].search([('bill_id', '=', name)])
            advance = 0
            paid = 0
            if len(mr)>2:
                for i in range(len(mr)-1):
                    advance=advance+mr[i].amount
                paid=mr[len(mr)-1].amount
            # mr_ids=self.pool.get('leih.money.receipt').search([('bill_id', '=', name)], context=context)

                lists={
                    'advance':advance,
                    'paid':paid
                }
            elif len(mr)==2:
                advance = advance + mr[0].amount
                paid = paid + mr[1].amount
                lists={
                    'advance':advance,
                    'paid':paid
                }
            elif len(mr)==1:
                advance = advance + mr[0].amount
                lists={
                    'advance':advance,
                    'paid':0
                }
            elif len(mr)<1:
                lists={
                    'advance':0,
                    'paid':0
                }

        # final_text = new_text.replace("Cent", "Paisa")
        return lists

    #if same item exist in line
    # @api.multi
    # @api.constrains('bill_register_line_id')
    # def _check_exist_item_in_line(self):
    #     for item in self:
    #         exist_item_list = []
    #         for line in item.bill_register_line_id:
    #             if line.name.id in exist_item_list:
    #                 raise ValidationError(_('Item should be one per line.'))
    #             exist_item_list.append(line.name.id)


    def bill_confirm(self, cr, uid, ids, context=None):

        stored_obj = self.browse(cr, uid, [ids[0]], context=context)
        journal_object=self.pool.get("bill.journal.relation")

        diagonostic_bill = stored_obj.diagonostic_bill
        ## Bill Status Will Change

        if stored_obj.state == 'confirmed':
            raise osv.except_osv(_('Warning!'),
                                 _('Already this Bill is Confirmed.'))

        #this section is used to minimum payment for bill 35%
        grand_total=stored_obj.grand_total
        paid_amount=stored_obj.paid
        if grand_total!=0:
            percent_amount=(paid_amount*100)/grand_total
        if grand_total==0:
            percent_amount=0
        if percent_amount>=25 or grand_total==0:

            stored = int(ids[0])

            ### check and merged with Lab report

            get_all_tested_ids = []

            for items in stored_obj.bill_register_line_id:
                get_all_tested_ids.append(items.name.id)


            ### Ends here merged Section

            already_merged = []
            custom_name=''
            for items in stored_obj.bill_register_line_id:
                custom_name = ''
                state = 'sample'
                ### Create LAB/SAMPLE From Here
                if items.name.sample_req == False or items.name.sample_req == None:
                    state='lab'

                if items.name.manual != True or items.name.lab_not_required != True:

                    custom_name = custom_name + ' ' + str(items.name.name)
                    if items.name.id not in already_merged:

                        child_list = []
                        value = {
                            'bill_register_id':int(stored),
                            'test_id':int(items.name.id),
                            'department_id':items.name.department.name,
                            'state':state
                        }

                        for test_item in items.name.examination_entry_line:

                            tmp_dict = {}
                            tmp_dict['test_name'] = test_item.name
                            tmp_dict['ref_value'] = test_item.reference_value
                            tmp_dict['bold']=test_item.bold
                            tmp_dict['group_by']=test_item.group_by
                            child_list.append([0, False, tmp_dict])

                        if items.name.merge == True:


                            for entry in items.name.merge_ids:
                                test_id=entry.examinationentry_id.id

                                if test_id in get_all_tested_ids:
                                    custom_name = custom_name + ', '+str(entry.examinationentry_id.name)
                                    already_merged.append(test_id)
                                    for m_test_line in entry.examinationentry_id.examination_entry_line:

                                        tmp_dict = {}
                                        tmp_dict['test_name'] = m_test_line.name
                                        tmp_dict['ref_value'] = m_test_line.reference_value
                                        tmp_dict['bold'] = m_test_line.bold
                                        tmp_dict['group_by'] = m_test_line.group_by
                                        child_list.append([0, False, tmp_dict])




                        value['sticker_line_id']=child_list

                        value['full_name']=custom_name


                        sample_obj = self.pool.get('diagnosis.sticker')
                        sample_id = sample_obj.create(cr, uid, value, context=context)

                    ### Ends Here LAB/SAMPLE From Here

                    if sample_id is not None:
                        sample_text = 'Lab-0' + str(sample_id)
                        cr.execute('update diagnosis_sticker set name=%s where id=%s', (sample_text, sample_id))
                        cr.commit()


            # import pdb
            # pdb.set_trace()

            has_been_paid = 0



                ### Journal ENtry will be here

            if stored_obj:
                line_ids = []

                if context is None: context = {}
                if context.get('period_id', False):
                    return context.get('period_id')
                periods = self.pool.get('account.period').find(cr, uid, context=context)
                period_id = periods and periods[0] or False
                # if method is cash
                if stored_obj.payment_type.name=='Cash':
                    has_been_paid = stored_obj.paid
                    ar_amount = stored_obj.due
                    account_id=6
                elif stored_obj.payment_type.name == 'Visa Card':
                    has_been_paid = stored_obj.to_be_paid
                    ar_amount = stored_obj.due
                    account_id=stored_obj.payment_type.account.id

                if ar_amount > 0:
                    line_ids.append((0, 0, {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'tax_amount': 0,
                        'name': stored_obj.name,
                        'currency_id': False,
                        'credit': 0,
                        'date_maturity': False,
                        'account_id': 195, ### Accounts Receivable ID
                        'debit': ar_amount,
                        'amount_currency': 0,
                        'partner_id': False,
                    }))

                if has_been_paid > 0:
                    line_ids.append((0, 0, {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'tax_amount': 0,
                        'name': stored_obj.name,
                        'currency_id': False,
                        'credit': 0,
                        'date_maturity': False,
                        'account_id': account_id,  ### Cash/Bank ID
                        'debit': has_been_paid,
                        'amount_currency': 0,
                        'partner_id': False,
                    }))

                for cc_obj in stored_obj.bill_register_line_id:
                    ledger_id=611
                    try:
                        ledger_id = cc_obj.name.accounts_id.id
                    except:
                        ledger_id= 611 ## Diagnostic Income Head , If we don't assign any Ledger

                    if context is None:
                        context = {}

                    line_ids.append((0, 0, {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'tax_amount': 0,
                        'name': cc_obj.name.name,
                        'currency_id': False,
                        'account_id': cc_obj.name.accounts_id.id,
                        'credit': cc_obj.total_amount,
                        'date_maturity': False,
                        'debit': 0,
                        'amount_currency': 0,
                        'partner_id': False,
                    }))
                    # end cash statement


                    # if payment type is card

                if stored_obj.service_charge > 0:
                    line_ids.append((0, 0, {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'tax_amount': 0,
                        'name':stored_obj.payment_type.name,
                        'currency_id': False,
                        'credit': stored_obj.service_charge,
                        'date_maturity': False,
                        'account_id': stored_obj.payment_type.service_charge_account.id,  ### Cash ID
                        'debit': 0,
                        'amount_currency': 0,
                        'partner_id': False,
                    }))


                        # end of card payment

                jv_entry = self.pool.get('account.move')

                j_vals = {'name': '/',
                          'journal_id': 2,  ## Sales Journal
                          'date': stored_obj.date,
                          'period_id': period_id,
                          'ref': stored_obj.name,
                          'line_id': line_ids
                          }

                saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                if saved_jv_id > 0:
                    journal_id = saved_jv_id
                    try:
                        jv_entry.button_validate(cr,uid, [saved_jv_id], context)
                        cr.execute("update bill_register set state='confirmed' where id=%s", (ids))
                        cr.commit()
                        journal_dict={'journal_id':journal_id,'bill_journal_relation_id':stored_obj.id}
                        journal_object.create(cr,uid,vals=journal_dict,context=context)
                        if stored_obj.paid != False:
                            for bills_vals in stored_obj:
                                # import pdb
                                # pdb.set_trace()
                                mr_value = {
                                    'date': stored_obj.date,
                                    'bill_id': int(stored),
                                    'amount': stored_obj.paid,
                                    'type': stored_obj.type,
                                    'p_type': 'advance',
                                    'bill_total_amount': stored_obj.total,
                                    'due_amount': stored_obj.due
                                }
                            mr_obj = self.pool.get('leih.money.receipt')
                            mr_id = mr_obj.create(cr, uid, mr_value, context=context)

                            if mr_id is not None:
                                mr_name = 'MR#' + str(mr_id)
                                cr.execute('update leih_money_receipt set name=%s,diagonostic_bill=%s where id=%s',
                                           (mr_name, diagonostic_bill, mr_id))
                                cr.commit()
                                bill_payment_obj = self.pool.get('bill.register.payment.line')
                                service_dict = {'date': stored_obj.date, 'amount': paid_amount, 'type': stored_obj.payment_type.name, 'bill_register_payment_line_id': stored,
                                                'money_receipt_id': mr_id}
                                bill_payment_id = bill_payment_obj.create(cr, uid, vals=service_dict, context=context)
                    except:
                        import pdb
                        pdb.set_trace()
                ### Ends the journal Entry Here


            return self.pool['report'].get_action(cr, uid, ids, 'leih.report_bill_register', context=context)
        else:
            raise osv.except_osv(_('Warning!'),
                                 _('PLease Pay minimum amount.'))





    def onchange_total(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('leih.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        return tests

    def onchange_patient(self,cr,uid,ids,name,context=None):
        tests={}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc={'mobile':dep_object.mobile,'address':dep_object.address,'age':dep_object.age,'sex':dep_object.sex}
        tests['value']=abc
        return tests

    def add_new_test(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'add_bill_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'add.bill',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'bill_id':ids[0],
                'default_price':500,
                # 'default_name':context.get('name', False),
                'default_total_amount':200,
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
    def button_dummy(self, cr, uid, ids, context=None):


        return True

    def bill_cancel(self, cr, uid, ids, context=None):

        ##### Cancel Journal And Unlink/ Delete all journals

        cr.execute("select id as jounral_id from account_move where ref = (select name from bill_register where id=%s limit 1)",(ids))
        joural_ids = cr.fetchall()
        context=context

        itm = [itm[0] for itm in joural_ids]
        if len(itm)>0:
            uid=1
            moves =self.pool.get('account.move').browse(cr, uid, itm, context=context)
            moves.button_cancel() ## Cancelling

            bill_journal_id = []
            # cr.execute("delete from bill_journal_relation where id in (select id from bill_journal_relation where journal_id in %s)",(tuple(itm)))
            user_q = "select id from bill_journal_relation where journal_id in %s"
            # cr.execute("select id from bill_journal_relation where journal_id in %s",(tuple(itm)))
            cr.execute(user_q, (tuple(itm),))
            journal_id = cr.fetchall()
            for item in journal_id:
                bill_journal_id.append(item[0])

            query = "delete from bill_journal_relation where id in %s"
            cr.execute(query, (tuple(bill_journal_id),))

            moves.unlink()  ### Deleting Journal



        #### Ends Here

        ## Bill Status Will Change

        cr.execute("update bill_register set state='cancelled' where id=%s", (ids))
        cr.commit()
        ## Lab WIll be Deleted

        cr.execute("update diagnosis_sticker set state='cancel' where bill_register_id=%s", (ids))
        cr.commit()

        #for updates on cash collection
        cr.execute("update leih_money_receipt set state='cancel' where bill_id=%s", (ids))
        cr.commit()




        return True

    def btn_pay_bill(self, cr, uid, ids, context=None):
        if not ids: return []
        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.state == 'pending':
            raise osv.except_osv(_('Warning'), _('Please Confirm and Print the Bill'))
        if inv.total <= inv.paid:
            raise osv.except_osv(_('Full Paid'), _('Nothing to Pay Here. Already Full Paid'))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih','bill_register_payment_form_view')
        #

        # total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'bill.register.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_bill_id': ids[0],
                'default_amount': inv.due
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def add_discount(self,cr,uid,ids,context=None):
        # import pdb
        # pdb.set_trace()
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'discount_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'discount',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'pi_id':ids[0]
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def create(self, cr, uid, vals, context=None):
        if vals.get("due"):
            if vals.get("due")<0:
                raise osv.except_osv(_('Warning!'),
                                     _("Check paid and grand total!"))

        if context is None:
            context = {}

        child_ids =["MRI",'X-Ray','Radiology & Imaging','Pathology','Bio-Chemistry','Haematology','Serology','Micro-Biology','CT Scan','USG','Diagnostic','X-Ray','Echocardiogram','Hormone','Immunology']

        ### Check Diagonostice Items available or not. If avvailable then no ther component will be there

        get_all_depts =[]
        if vals.get('bill_register_line_id'):
            for items in vals.get('bill_register_line_id'):
                if items[2].get('department'):
                    if items[2].get('department') not in get_all_depts:
                        get_all_depts.append(items[2].get('department'))

        ## Check Diagnsis exists
        mixed_up = False
        vals['diagonostic_bill'] = False

        intersection_result = list(set(child_ids) & set(get_all_depts))
        if len(intersection_result)>0 and len(intersection_result) == len(get_all_depts):
            mixed_up = False
            vals['diagonostic_bill'] = True
        elif len(intersection_result)>0 and  len(intersection_result) != len(get_all_depts):
            mixed_up=True

        if mixed_up == True:
            raise osv.except_osv(_('Attention'),
                                 _('This investigation has diagnosis and others department mix up'))


        ### Ends Here Diagonostic Items
        #
        #
        # import pdb
        # pdb.set_trace()

        stored = super(bill_register, self).create(cr, uid, vals, context) # return ID int object


        if stored is not None:
            name_text = 'Bill-0' + str(stored)
            cr.execute('update bill_register set name=%s where id=%s', (name_text, stored))
            cr.commit()
        return stored

    def write(self, cr, uid, ids,vals,context=None):
        if vals.get("due"):
            if vals.get("due")<0:
                raise osv.except_osv(_('Warning!'),
                                     _("Check paid and grand total!"))


        if vals.get('bill_register_line_id') or uid == 1:
            cr.execute("select id as journal_ids from account_move where ref = (select name from bill_register where id=%s limit 1)",(ids))
            journal_ids = cr.fetchall()
            context=context
            updated = super(bill_register, self).write(cr, uid, ids, vals, context=context)
            itm = [itm[0] for itm in journal_ids]
            # import pdb
            # pdb.set_trace()

            if len(itm)>0:

                uid=1
                moves =self.pool.get('account.move').browse(cr, uid, itm, context=context)
                xx=moves.button_cancel() ## Cancelling
                bill_journal_id=[]
                # cr.execute("delete from bill_journal_relation where id in (select id from bill_journal_relation where journal_id in %s)",(tuple(itm)))
                user_q="select id from bill_journal_relation where journal_id in %s"
                # cr.execute("select id from bill_journal_relation where journal_id in %s",(tuple(itm)))
                cr.execute(user_q, (tuple(itm),))
                journal_id = cr.fetchall()
                for item in journal_id:
                    bill_journal_id.append(item[0])

                query="delete from bill_journal_relation where id in %s"
                cr.execute(query,(tuple(bill_journal_id),))




                # if len(itm)>1:
                #     cr.execute("delete from bill_journal_relation where id = (select id from bill_journal_relation where journal_id=%s)", ([itm[0]]))
                #     cr.execute("delete from bill_journal_relation where id = (select id from bill_journal_relation where journal_id=%s)", ([itm[1]]))
                #     cr.commit()
                # else:
                #     cr.execute("delete from bill_journal_relation where id = (select id from bill_journal_relation where journal_id=%s)",(itm))

                # import pdb
                # pdb.set_trace()

                moves.unlink()
                #journal entry will be here


                    ### Journal ENtry will be here

                stored_obj = self.browse(cr, uid, [ids[0]], context=context)
                journal_object = self.pool.get("bill.journal.relation")
                if stored_obj:
                    line_ids = []

                    if context is None: context = {}
                    if context.get('period_id', False):
                        return context.get('period_id')
                    periods = self.pool.get('account.period').find(cr, uid, context=context)
                    period_id = periods and periods[0] or False
                    has_been_paid = stored_obj.paid
                    ar_amount = stored_obj.due

                    if ar_amount > 0:
                        line_ids.append((0, 0, {
                            'analytic_account_id': False,
                            'tax_code_id': False,
                            'tax_amount': 0,
                            'name': stored_obj.name,
                            'currency_id': False,
                            'credit': 0,
                            'date_maturity': False,
                            'account_id': 195, ### Accounts Receivable ID
                            'debit': ar_amount,
                            'amount_currency': 0,
                            'partner_id': False,
                        }))

                    if has_been_paid > 0:
                        line_ids.append((0, 0, {
                            'analytic_account_id': False,
                            'tax_code_id': False,
                            'tax_amount': 0,
                            'name': stored_obj.name,
                            'currency_id': False,
                            'credit': 0,
                            'date_maturity': False,
                            'account_id': 6,  ### Cash ID
                            'debit': has_been_paid,
                            'amount_currency': 0,
                            'partner_id': False,
                        }))

                    for cc_obj in stored_obj.bill_register_line_id:
                        ledger_id=611
                        try:
                            ledger_id = cc_obj.name.accounts_id.id
                        except:
                            ledger_id= 611 ## Diagnostic Income Head , If we don't assign any Ledger



                        if context is None:
                            context = {}

                        line_ids.append((0, 0, {
                            'analytic_account_id': False,
                            'tax_code_id': False,
                            'tax_amount': 0,
                            'name': cc_obj.name.name,
                            'currency_id': False,
                            'account_id': cc_obj.name.accounts_id.id,
                            'credit': cc_obj.total_amount,
                            'date_maturity': False,
                            'debit': 0,
                            'amount_currency': 0,
                            'partner_id': False,
                        }))




                    jv_entry = self.pool.get('account.move')

                    j_vals = {'name': '/',
                              'journal_id': 2,  ## Sales Journal
                              'date': stored_obj.date,
                              'period_id': period_id,
                              'ref': stored_obj.name,
                              'line_id': line_ids

                              }

                    saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                    if saved_jv_id > 0:
                        journal_id = saved_jv_id
                        try:
                            jv_entry.button_validate(cr,uid, [saved_jv_id], context)
                            cr.execute("update bill_register set state='confirmed' where id=%s", (ids))
                            cr.commit()
                            journal_dict={'journal_id':journal_id,'bill_journal_relation_id':stored_obj.id}
                            journal_object.create(cr,uid,vals=journal_dict,context=context)
                        except:
                            import pdb
                            pdb.set_trace()
                    return updated
                    ### Ends the journal Entry Here
            else:
                updated = super(bill_register, self).write(cr, uid, ids, vals, context=context)
                # raise osv.except_osv(_('Warning!'),
                #                      _("You cannot Edit the bill"))
                return updated



    @api.onchange('bill_register_line_id')
    def onchange_test_bill(self):
        sumalltest=0
        total_without_discount=0
        for item in self.bill_register_line_id:
            sumalltest=sumalltest+item.total_amount
            total_without_discount=total_without_discount+item.price

        self.total=sumalltest
        after_dis = (sumalltest* (self.doctors_discounts/100))
        self.after_discount = 0

        self.grand_total=sumalltest
        self.due=sumalltest- self.paid
        self.total_without_discount=total_without_discount
        # import pdb
        # pdb.set_trace()
        #

        return "X"

    @api.onchange('paid')
    def onchange_paid(self):
        self.due = self.grand_total - self.paid
        if self.payment_type:
            if self.payment_type.name=='Visa Card':
                interest = self.payment_type.service_charge
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
        return 'x'



    @api.onchange('doctors_discounts')
    def onchange_doc_discount(self):
        discount = self.doctors_discounts

        for item in self.bill_register_line_id:
            item.discount_percent=round((item.price*discount)/100)
            item.discount=discount
            item.total_discount = item.flat_discount + item.discount_percent
            item.total_amount = item.price - item.total_discount


            # if item.discount>0:
            #     dis = round(item.price * discount / 100)
            #     dis_amount=round(item.price-dis)
            #     item.discount=discount
            #     item.total_discount=item.price-item.total_amount
            #     item.total_amount=dis_amount
            #
            # elif item.flat_discount>0 or item.discount<=0:
            #     dis = round(item.total_amount * discount / 100)
            #     dis_amount = round(item.total_amount - dis)
            #     item.discount = discount
            #     item.total_discount = item.price-item.total_amount
            #     item.total_amount = dis_amount
        return "X"

    @api.onchange('other_discount')
    def onchange_other_discount(self):
        other_discount = self.other_discount
        total=self.total_without_discount
        if total>0:
            discount_distribution=other_discount/total
            for item in self.bill_register_line_id:
                item.flat_discount=0
                item.flat_discount=round(item.price*discount_distribution)
                item.total_discount=item.flat_discount+item.discount_percent
                item.total_amount=item.price-item.total_discount










            # discount_dec=other_discount/total
            # discount_figure=1-discount_dec
            #
            # for item in self.bill_register_line_id:
            #     dis_amount = round(item.price*discount_figure)
            #     item.flat_discount =round((item.price-dis_amount))
            #     item.total_discount = round(item.flat_discount+item.discount)
            #     item.total_amount =dis_amount

        #
        #
        #
        #
        # self.grand_total = self.total - self.other_discount
        # self.due=self.total - self.other_discount- self.paid
        return 'Y'






class test_information(osv.osv):
    _name = 'bill.register.line'



    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('bill.register')
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rate=record.price
            discount=record.discount
            interst_amount=int(discount)*int(rate)/100
            total_amount=int(rate)-interst_amount
            res[record.id]=total_amount
            # import pdb
            # pdb.set_trace()
        return res




    _columns = {

        'name': fields.many2one("examination.entry","Item Name",ondelete='cascade'),
        'bill_register_id': fields.many2one('bill.register', "Information"),
        'department':fields.char("Department"),
        'delivery_date':fields.date("Delivery Date"),
        'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount (%)"),
        'flat_discount': fields.integer("Flat Discount"),
        'total_discount': fields.integer("Total Discount"),
        'discount_percent':fields.integer("Discount Percent"),
        'total_amount': fields.integer("Total Amount"),
        'assign_doctors': fields.many2one('doctors.profile', 'Doctor'),
        'commission_paid': fields.boolean("Commission Paid"),
    }

    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        #code for delivery date

        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        delivery_required_days=dep_object.required_time
        delivery_date=date.today() + timedelta(days=delivery_required_days)
        # import pdb
        # pdb.set_trace()
        abc = {'department':dep_object.department.name,'price': dep_object.rate,'total_amount':dep_object.rate,'bill_register_id.paid':dep_object.rate,'delivery_date':delivery_date}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_discount(self,cr,uid,ids,price,discount,context=None):
        tests = {'values': {}}

        dis_amount = round(price-(price* discount/100))

        abc = {'total_amount':dis_amount, 'total_discount':dis_amount}
        tests['value'] = abc

        return tests
    def create(self, cr, uid, vals, context=None):
        # deliry_min_time
        stored = super(test_information, self).create(cr, uid, vals, context)
        bill_register_line_object=self.browse(cr, uid, stored, context=context)
        test_name=bill_register_line_object.name
        required_time=test_name.required_time
        today = date.today()
        delivery_date=today+timedelta(days=required_time)
        cr.execute("update bill_register_line set delivery_date=%s where id=%s", (delivery_date,stored))
        cr.commit()

        # today = datetime.datetime.strftime(datetime.datetime.today(), '%d/%m/%Y-%Hh/%Mm')

        return 0

    # def write(self, cr, uid, vals, context=None):
    #     import pdb
    #     pdb.set_trace()

class admission_payment_line(osv.osv):
    _name = 'bill.register.payment.line'

    _columns = {
        'bill_register_payment_line_id': fields.many2one('bill.register', 'bill register payment'),
        'date':fields.date("Date"),
        'amount':fields.float('Amount'),
        'type':fields.char("Type"),
        'card_no':fields.char('Card Number'),
        'bank_name':fields.char('Bank Name'),
        'money_receipt_id': fields.many2one('leih.money.receipt', 'Money Receipt ID'),

    }

class bill_journal_relations(osv.osv):
    _name = 'bill.journal.relation'

    _columns = {
        'bill_journal_relation_id': fields.many2one('bill.register', 'bill register payment'),
        'admission_journal_relation_id': fields.many2one('leih.admission', 'Admission Journal'),
        'journal_id': fields.integer("Journal Id"),
    }


# class accoun_move(osv.osv):
#     _inherit ="account.move"
#
#     def write(self, cr, uid,ids, vals, context=None):
#         import pdb
#         pdb.set_trace()







