from openerp.tools.translate import _
from openerp import api, exceptions, models
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from datetime import date, time
from openerp.tools.amount_to_text_en import amount_to_text
from datetime import date, time, timedelta, datetime


# PACKAGE_FIELDS=('name','price')

class leih_hospital_admission(osv.osv):
    _name = "hospital.admission"
    _order = 'id desc'

    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("hospital.admission").browse(cr, uid, ids, context=None):
            total_list = []
            for amount in items.leih_admission_line_id:
                total_list.append(amount.total_amount)
            for item in total_list:
                sum = item + sum
                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum
                    # import pdb
                    # pdb.set_trace()
        return Percentance_calculation

    def _default_payment_type(self):
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name': fields.char("Name"),
        'mobile': fields.char(string="Mobile", store=False),
        'patient_id': fields.char(related='patient_name.patient_id', string="Patient Id"),
        'patient_name': fields.many2one('patient.info', "Patient Name", required=True),
        'address': fields.char("Address", store=False),
        'age': fields.char("Age", store=False),
        'sex': fields.char("Sex", store=False),
        'ref_doctors': fields.many2one('doctors.profile', 'Reffered by (Doctor)'),
        'operation_date': fields.date("Operation Date"),
        'package_name': fields.many2one("examine.package", string="Package"),

        'leih_admission_line_id': fields.one2many('hospital.admission.line', 'leih_admission_id', 'Investigations'),

        'guarantor_line_id': fields.one2many("hospital.patient.guarantor", "admission_id", "Guarantor Name"),

        'bill_register_admission_line_id': fields.one2many("bill.register.general.admission.line",
                                                           "general_admission_line_id", "Bill Register"),

        'admission_payment_line_id': fields.one2many("general.admission.payment.line", "admission_payment_line_id",
                                                     "Admission Payment"),

        'admission_journal_relation_id': fields.one2many("bill.journal.relation",
                                                         "general_admission_journal_relation_id", "Journal"),

        'hospital_doctor_line_id': fields.one2many("doctor.profile.admission.line", "hospital_doctor_line_item",
                                                   "Doctor"),

        'prescription_id': fields.one2many("indoor.pos.order", "prescription_item", "Prescription"),

        'return_prescription_id': fields.one2many("return.indoor.pos.order", "return_prescription_item","Return Prescription"),

        'hospital_medicine_line_id': fields.one2many("hospital.medicine.line", "hospital_medicine_line_item",
                                                     "Investigations"),

        'hospital_bed_line_id': fields.one2many("hospital.bed.line", "hospital_bed_item_id", "Bed"),
        'hospital_bill_line_id': fields.one2many("hospital.bill.line", "hospital_admission_id", "Bill"),

        'emergency': fields.boolean("Emergency Department"),
        'total_without_discount': fields.float(string="Total without discount"),
        'total': fields.float(string="Total"),

        'medicine_total': fields.float(string="Medicine Total"),
        'return_medicine_total': fields.float(string="Return Medicine Total"),
        'adjust_medicine_total': fields.float(string="Adjust Medicine Total"),

        'doctors_discounts': fields.float("Discount(%)"),
        'after_discount': fields.float("Discount Amount"),
        'other_discount': fields.float("Other Discount"),
        'discount_remarks': fields.char("Discount Remarks"),
        'grand_total': fields.float("Grand Total"),
        'investigation_total': fields.float('Investigation Total'),
        'investigation_paid': fields.float('Investigation Paid'),
        'advance': fields.float("Advance"),
        'paid': fields.float("Paid"),
        'due': fields.float("Due"),
        'type': fields.selection([('cash', 'Cash'), ('bank', 'Bank')], 'Payment Type'),
        'card_no': fields.char('Card No.'),
        'bank_name': fields.char('Bank Name'),
        'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
        'user_id': fields.many2one('res.users', 'Assigned to', select=True, track_visibility='onchange'),
        'state': fields.selection(
            [('pending', 'Pending'), ('activated', 'Admitted'), ('released', 'Released'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True,
        ),
        'emergency_covert_time': fields.datetime("Admission Convert time"),
        'old_journal': fields.boolean("Old Journal"),
        # payment type attributes
        'payment_type': fields.many2one("payment.type", "Payment Type", default=_default_payment_type),
        'service_charge': fields.float("Service Charge"),
        'to_be_paid': fields.float("To be Paid"),
        'account_number': fields.char("Account Number"),
        # added for general
        'father_name': fields.char("Father's Name"),
        'mother_name': fields.char("Mother's Name"),
        'spouse_name': fields.char("Spouse's Name"),
        'religion': fields.selection(
            [('islam', 'Islam'), ('hindu', 'Hinduism'), ('buddhism', 'Buddhism'), ('christianity', 'Christianity')],
            'Religion'),
        'blood_group': fields.char('Blood Group'),
        # 'reffered_to_hospital': fields.char('Refferred to this hospital by'),
        'reffered_to_hospital': fields.many2one('brokers.info', 'Referral'),
        'occupation': fields.char('Occupation'),
        'business_address': fields.char('Business Address'),
        'admitting_doctor': fields.many2one('doctors.profile', 'Admitting Doctor'),
        # hospital use only ----------------------------------------------------------------
        'bed': fields.char('Bed/Cabin'),
        # 'bed_no': fields.char(' No'),
        # 'cabin_no': fields.char('Cabin`'),
        'received_by': fields.char('Received/Registered By'),
        'clinic_diagnosis': fields.char('Clinical Diagnosis'),
        'release_note_date': fields.datetime("Release Date", readonly=True),
        'release_note': fields.text("Release Note"),
        'release_approved_by': fields.many2one('doctors.profile', "Release Approved By:"),
    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
    }

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active == True:
            interest = self.payment_type.service_charge
            if interest > 0:
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
            else:
                self.to_be_paid = self.paid
                self.service_charge = 0
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
    def advance_paid(self, name):
        mr = self.env['legh.money.receipt'].search([('general_admission_id', '=', name)])
        advance = 0
        paid = 0
        if len(mr) > 2:
            for i in range(len(mr) - 1):
                advance = advance + mr[i].amount
            paid = mr[len(mr) - 1].amount
            # mr_ids=self.pool.get('leih.money.receipt').search([('bill_id', '=', name)], context=context)

            lists = {
                'advance': advance,
                'paid': paid
            }
        elif len(mr) == 2:
            advance = advance + mr[0].amount
            paid = paid + mr[1].amount
            lists = {
                'advance': advance,
                'paid': paid
            }
        elif len(mr) == 1:
            advance = advance + mr[0].amount
            lists = {
                'advance': advance,
                'paid': 0
            }
        elif len(mr) == 0:
            advance = advance
            lists = {
                'advance': advance,
                'paid': 0
            }

        # final_text = new_text.replace("Cent", "Paisa")
        return lists

    # def calculate_bill(self, cr, uid, ids, context=None):
    #     bill_dict=[]
    #     bill_ids = self.pool.get("bill.register").search(cr,uid,[('general_admission_id', '=', ids[0]),('state','=','confirmed')],context=None)
    #     bill_obj = self.pool.get('bill.register').browse(cr, uid, bill_ids, context=None)
    #     hospital_admission_line_obj = self.pool.get('hospital.bill.line')
    #     hospital_admission_obj = self.browse(cr, uid, ids[0], context=context)
    #     investigation_paid=0
    #     investigation_total = 0
    #     for obj in bill_obj:
    #         if obj.is_applied_to_admission != True:
    #             investigation_paid=investigation_paid+obj.paid
    #             values = {}
    #             for item in obj.bill_register_line_id:
    #                 values={
    #                     'item_name':item.name.id,
    #                     'product_qty':1,
    #                     'price':item.price,
    #                     'discount':item.discount,
    #                     'total_discount':item.total_discount,
    #                     'total_amount':item.total_amount,
    #                     'bill_created_date':item.create_date,
    #                     'hospital_admission_id':ids[0]
    #                 }
    #                 bill_ids = hospital_admission_line_obj.create(cr, uid, vals=values, context=context)
    #                 hospital_admission_obj.onchange_admission_line()
    #                 investigation_total=investigation_total+item.total_amount
    #             obj.is_applied_to_admission = True
    #     hospital_admission_obj.investigation_total=hospital_admission_obj.investigation_total+investigation_total
    #     hospital_admission_obj.investigation_paid=hospital_admission_obj.investigation_paid+investigation_paid
    #     hospital_admission_obj.onchange_paid()
    #
    #     return bill_ids



    def calling_all_indor_pos_with_status(self,  cr, uid, ids, context=None):

        ##general_addmission_id
        bill_ids = self.pool.get("indoor.pos.order").search(cr, uid, [('general_admission_id', '=', self.id),
                                                                   ('state', '!=', 'cancel')], context=None)

        p_line_ids = [itm.id for itm in self.prescription_id]
        # p_line_ids.append(self_obj.id)
        self.prescription_id = p_line_ids
        return True
    def calculate_bill(self, cr, uid, ids, context=None):
        bill_dict = []
        total_medicine_bill = 0
        total_medicine_return_bill=0

        pres_ids = self.pool.get("indoor.pos.order").search(cr, uid, [('general_admission_id', '=', ids[0]),('state', '!=', 'cancel')], context=None)
        bill_ids = self.pool.get("bill.register").search(cr, uid, [('general_admission_id', '=', ids[0]),
                                                                   ('state', '=', 'confirmed')], context=None)
        bill_obj = self.pool.get('bill.register').browse(cr, uid, bill_ids, context=None)
        hospital_admission_line_obj = self.pool.get('hospital.bill.line')
        hospital_admission_obj = self.browse(cr, uid, ids[0], context=context)

        if len(pres_ids)>0:
            hospital_admission_obj.prescription_id = pres_ids

        previous_adjust_medicine_total=hospital_admission_obj.adjust_medicine_total
        if hospital_admission_obj.prescription_id:
            for item in hospital_admission_obj.prescription_id:
                total_medicine_bill+=item.amount_total
        if hospital_admission_obj.return_prescription_id:
            for item in hospital_admission_obj.return_prescription_id:
                total_medicine_return_bill+=item.amount_total
        hospital_admission_obj.medicine_total=total_medicine_bill
        hospital_admission_obj.return_medicine_total=total_medicine_return_bill
        hospital_admission_obj.adjust_medicine_total=total_medicine_bill - total_medicine_return_bill
        if previous_adjust_medicine_total!=hospital_admission_obj.adjust_medicine_total:
            hospital_admission_obj.onchange_medicine()
        # hospital_admission_obj.grand_total = hospital_admission_obj.total + total_medicine_bill - total_medicine_return_bill


        investigation_paid = 0
        investigation_total = 0
        for obj in bill_obj:
            if obj.is_applied_to_admission != True:
                investigation_paid = investigation_paid + obj.paid
                values = {}
                for item in obj.bill_register_line_id:
                    existing_item = hospital_admission_line_obj.search(cr, uid, [('item_name', '=', item.name.id), (
                        'bill_created_date', '=', item.create_date), ('hospital_admission_id', '=', ids[0])],
                                                                       context=context)
                    if not existing_item:
                        values = {
                            'item_name': item.name.id,
                            'product_qty': 1,
                            'price': item.price,
                            'discount': item.discount,
                            'total_discount': item.total_discount,
                            'total_amount': item.total_amount,
                            'bill_created_date': item.create_date,
                            'hospital_admission_id': ids[0]
                        }
                        bill_ids = hospital_admission_line_obj.create(cr, uid, vals=values, context=context)
                        hospital_admission_obj.onchange_admission_line()
                        investigation_total = investigation_total + item.total_amount
                    else:
                        bill_ids = existing_item[0]
                obj.is_applied_to_admission = True
        hospital_admission_obj.investigation_total = hospital_admission_obj.investigation_total + investigation_total
        hospital_admission_obj.investigation_paid = hospital_admission_obj.investigation_paid + investigation_paid
        hospital_admission_obj.onchange_paid()

        return bill_ids

    @api.onchange('medicine_total','return_medicine_total')
    def onchange_medicine(self):
        # self.total+=self.medicine_total
        # self.total-=self.return_medicine_total

        self.grand_total=self.grand_total + self.medicine_total - self.return_medicine_total
        self.total=self.total + self.medicine_total - self.return_medicine_total
        self.total_without_discount=self.total_without_discount + self.medicine_total - self.return_medicine_total
        # self.total_without_discount+=self.medicine_total
        # self.total_without_discount-=self.return_medicine_total

    def onchange_total(self, cr, uid, ids, name, context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('legh.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        return tests

    # def print_bill_register(self, cr, uid, ids, context=None):
    #     '''
    #     This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
    #     '''
    #     assert len(ids) == 1, 'This option should only be used for a single id at a time'
    #
    #     return self.pool['report'].get_action(cr, uid, ids, 'sale.report_saleorder', context=context)

    def onchange_patient(self, cr, uid, ids, name, context=None):
        tests = {}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc = {'mobile': dep_object.mobile, 'address': dep_object.address, 'age': dep_object.age, 'sex': dep_object.sex}
        tests['value'] = abc
        return tests

    # def _package_fields(self, cr, uid, context=None):
    #     return list(PACKAGE_FIELDS)

    # def onchange_mobile(self,cr,uid,ids,mobile,context=None):
    #     tests={'values':{}}
    #     patient_id=self.pool.get('patient.info').search(cr,uid,[('mobile', '=', mobile)],context=None)
    #     dep_object=self.pool.get('patient.info').browse(cr,uid,patient_id,context)
    #     abc = {'patient': dep_object.name, 'address': dep_object.address, 'age': dep_object.age, 'sex': dep_object.sex}
    #     tests['value']=abc
    #     return tests

    #
    # import pdb
    # pdb.set_trace()

    def onchange_package(self, cr, uid, ids, package_name, vals, context=None):
        values = {}
        if not package_name:
            return {}
        total_amount = 0.0
        abc = {'leih_admission_line_id': []}
        package_object = self.pool.get('examine.package').browse(cr, uid, package_name, context=None)
        abc['other_discount'] = package_object.total_without_discount - package_object.total

        for item in package_object.examine_package_line_id:
            items = item.name.id
            total_amount = total_amount + item.total_amount

            abc['leih_admission_line_id'].append([0, False, {'name': item.name.id, 'total_amount': item.total_amount,
                                                             'price': item.price, 'flat_discount': item.discount}])
        values['value'] = abc
        return values

    def journal_line_formation(self,debit=0, credit=0,account_id=None,remarks=""):
        result_dict ={
            'analytic_account_id': False,
            'tax_code_id': False,
            'tax_amount': 0,
            'name': remarks,
            'currency_id': False,
            'credit': credit,
            'date_maturity': False,
            'account_id': account_id,  ### Accounts Receivable ID
            'debit': debit,
            'amount_currency': 0,
            'partner_id': False,

        }

        return result_dict


    def create_custom_journal(self,cr,uid,ref='',line_ids=[],date=None,context=None):
        j_id=1
        # if context.get('period_id', False):
        #     return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, dt=date)
        # import pdb
        # pdb.set_trace()
        period_id = periods and periods[0] or False
        jv_entry = self.pool.get('account.move')


        j_vals = {'name': '/',
                  'journal_id': 2,  ## Sales Journal
                  'date': fields.date.today(),
                  'period_id': period_id,
                  'ref': ref,
                  'line_id': line_ids

                  }
        j_id = jv_entry.create(cr, 1, j_vals, context=context)

        return j_id


    # This Function is used for the Released Admission
    def btn_final_settlement(self, cr, uid, ids, context=None):

        for record in self.browse(cr, uid, ids, context=context):
            # import pdb
            # pdb.set_trace()
            ## check all Prescribtions are confirmed or Not

            for pre_item in record.prescription_id:
                if pre_item.state == 'draft':
                    raise osv.except_osv("Prescription", "Please Close all Prescription by Pharmacy.\n Contact With Them")


            if record.state == 'activated' or record.state == 'released':
                if record.due > 0:
                    raise osv.except_osv("Bill DUE", "Please Pay the Due Bill")
                if not record.release_note:
                    raise osv.except_osv("Release Note", "Please give the description about the release note field")
                if record.state == 'released' or record.state == 'activated':
                    # self.write(cr, uid, [record.id], {'state': 'released'}, context=context)
                    # self.write(cr, uid, [record.id], {'release_note_date': datetime.now()})
                    ##### Insert Journal here for ALl



                    journal_items = []
                    admission_name = record.name
                    total_AR_income = 0
                    consult_amnt=0

                    for itm in record.hospital_doctor_line_id:
                        consult_amnt += itm.total_amount
                        if consult_amnt >0:
                            total_AR_income += itm.total_amount

                        try:
                            income_account_id = itm.name.accounts_id.id
                        except:
                            income_account_id = 9188  ## Doctor Consultation Fees

                        journal_items.append((0, 0, self.journal_line_formation(debit=0, credit=consult_amnt,
                                                                                account_id=income_account_id,
                                                                                remarks=admission_name)))


                    for itm in record.leih_admission_line_id:
                        credit_amount =itm.total_amount
                        if credit_amount>0:
                            total_AR_income +=itm.total_amount
                            try:
                                income_account_id = itm.name.accounts_id.id
                            except:
                                income_account_id = 8629 ## If we don't find any account it will automatically assign to this income account

                            journal_items.append((0, 0, self.journal_line_formation(debit=0,credit=credit_amount,
                                                                                    account_id=income_account_id,
                                                                                    remarks=admission_name)))

                    if record.adjust_medicine_total >0:
                        journal_items.append((0, 0, self.journal_line_formation(debit=0, credit=record.adjust_medicine_total,
                                                                                account_id=1780,
                                                                                remarks=admission_name)))
                        total_AR_income +=record.adjust_medicine_total


                    if record.other_discount >0:
                        if record.discount_remarks is False:
                            dis_name = "Discount"
                        else:
                            dis_name = str(record.discount_remarks) + " - "
                        journal_items.append((0, 0, self.journal_line_formation(debit=record.other_discount, credit=0,
                                                                                account_id=9071, #9175
                                                                                remarks=dis_name)))
                        total_AR_income -=record.other_discount

                    if total_AR_income >0:
                        journal_items.append((0, 0, self.journal_line_formation(debit=total_AR_income, credit=0,
                                                                                account_id=771,
                                                                                remarks=admission_name)))



                    if len(journal_items)>1:
                        if record.x_income_journal != True:
                            admission_date = record.date
                            j_id = self.create_custom_journal(cr=cr,uid=uid,ref=admission_name,date=admission_date,line_ids=journal_items)

                            self.write(cr, uid, [record.id], {'state': 'released','x_income_journal':True}, context=context)
                        else:
                            raise osv.except_osv("Contact IT", "Please Contact With Kazi/Mufti")






                    #### Ends Here



            else:
                raise osv.except_osv("Error", "Please confirm the admission before releasing it.")
        return True

    def hospital_change_status(self, cr, uid, ids, context=None):
        stored_obj = self.browse(cr, uid, [ids[0]], context=context)
        ## Bill Status Will Change: ------------------
        if stored_obj.state == 'activated' or stored_obj.state == 'released':
            raise osv.except_osv(_('Warning!'),
                                 _('Already this Bill is Confirmed.'))
        try:
            cr.execute("update hospital_admission set state='activated' where id=%s", (ids))
            cr.commit()

            return self.pool['report'].get_action(cr, uid, ids, 'legh.general_report_admission', context=context)
        except:
            raise osv.except_osv(_('Warning!'),
                                 _('Something went wrong with this bill.'))

    def admission_cancel(self, cr, uid, ids, context=None):

        # unlink journal items
        cr.execute(
            "select  id as jounral_id from account_move where ref = (select name from hospital_admission where id=%s "
            "limit 1)",
            (ids))
        joural_ids = cr.fetchall()
        context = context

        itm = [itm[0] for itm in joural_ids]
        if len(itm) > 0:
            uid = 1
            moves = self.pool.get('account.move').browse(cr, uid, itm, context=context)
            moves.button_cancel()  ## Cancelling
            moves.unlink()  ### Deleting Journal
        ## Bill Status Will Change

        cr.execute("update hospital_admission set state='cancelled' where id=%s", (ids))
        cr.commit()
        ## Lab WIll be Deleted

        # cr.execute("update diagnosis_sticker set state='cancel' where bill_register_id=%s", (ids))
        # cr.commit()

        # for updates on cash collection
        cr.execute("update leih_money_receipt set state='cancel' where general_admission_id=%s", (ids))
        cr.commit()
        return True

    def add_new_test(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'add_bill_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'add.bill',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'leih_admission_id': ids[0]

                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    def btn_pay(self, cr, uid, ids, context=None):
        if not ids: return []

        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.state == 'pending' or inv.state == 'cancelled':
            raise osv.except_osv(_('Warning'), _('Please Confirm and Print the Bill'))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legh',
                                                                             'admission_general_payment_form_view')
        #

        # total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hospital.admission.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_admission_id': ids[0],
                'default_amount': inv.due
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    # -------------------------------------------------------------------------------------------------------------------------
    def add_discount(self, cr, uid, ids, context=None):
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
                'pi_id': ids[0]
                # 'default_price': 500,
                # # 'default_name':context.get('name', False),
                # 'default_total_amount': 200,
                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    def create(self, cr, uid, vals, context=None):
        if vals.get("due"):
            if vals.get("due") < 0:
                raise osv.except_osv(_('Warning!'),
                                     _("Check paid and grand total!"))

        if context is None:
            context = {}
        # import pdb
        # pdb.set_trace()
        stored = super(leih_hospital_admission, self).create(cr, uid, vals, context)  # return ID int object

        if vals.get("emergency") == False:

            if stored is not None:
                name_text = 'HA-0' + str(stored)
                cr.execute('update hospital_admission set name=%s where id=%s', (name_text, stored))
                cr.commit()
        else:
            if stored is not None:
                name_text = 'E-0' + str(stored)
                cr.execute('update hospital_admission set name=%s where id=%s', (name_text, stored))
                cr.commit()

        return stored

    def write(self, cr, uid, ids, vals, context=None):

        # if vals.get("due"):
        #     if vals.get("due")<0:
        #         raise osv.except_osv(_('Warning!'),
        #                              _("Check paid and grand total!"))
        #
        # if vals.get('leih_admission_line_id') or uid == 1:
        #     cr.execute("select id as journal_ids from account_move where ref = (select name from hospital_admission where id=%s limit 1)",(ids))
        #     journal_ids = cr.fetchall()
        #     context=context
        #
        #
        #     itm = [itm[0] for itm in journal_ids]
        #
        #     if len(itm)>0:
        #
        #         uid=1
        #         moves =self.pool.get('account.move').browse(cr, uid, itm, context=context)
        #         xx=moves.button_cancel() ## Cancelling
        #         bill_journal_id=[]
        #         # cr.execute("delete from bill_journal_relation where id in (select id from bill_journal_relation where journal_id in %s)",(tuple(itm)))
        #         user_q="select id from bill_journal_relation where journal_id in %s"
        #         cr.execute(user_q, (tuple(itm),))
        #         journal_id = cr.fetchall()
        #         for item in journal_id:
        #             bill_journal_id.append(item[0])
        #
        #         if len(bill_journal_id)>0:
        #             query="delete from bill_journal_relation where id in %s"
        #             cr.execute(query,(tuple(bill_journal_id),))
        #
        #         moves.unlink()
        #         updated=super(leih_hospital_admission, self).write(cr, uid, ids, vals, context=context)
        #         #journal entry will be here
        #
        #
        #             ### Journal ENtry will be here
        #
        #         stored_obj = self.browse(cr, uid, [ids[0]], context=context)
        #         journal_object = self.pool.get("bill.journal.relation")
        #         has_been_paid = stored_obj.paid
        #         if stored_obj:
        #             line_ids = []
        #
        #             if context is None: context = {}
        #             if context.get('period_id', False):
        #                 return context.get('period_id')
        #             periods = self.pool.get('account.period').find(cr, uid, context=context)
        #             period_id = periods and periods[0] or False
        #             ar_amount = stored_obj.due
        #
        #             if ar_amount > 0:
        #                 line_ids.append((0, 0, {
        #                     'analytic_account_id': False,
        #                     'tax_code_id': False,
        #                     'tax_amount': 0,
        #                     'name': stored_obj.name,
        #                     'currency_id': False,
        #                     'credit': 0,
        #                     'date_maturity': False,
        #                     'account_id': 195, ### Accounts Receivable ID
        #                     'debit': ar_amount,
        #                     'amount_currency': 0,
        #                     'partner_id': False,
        #                 }))
        #
        #             if has_been_paid > 0:
        #                 line_ids.append((0, 0, {
        #                     'analytic_account_id': False,
        #                     'tax_code_id': False,
        #                     'tax_amount': 0,
        #                     'name': stored_obj.name,
        #                     'currency_id': False,
        #                     'credit': 0,
        #                     'date_maturity': False,
        #                     'account_id': 6,  ### Cash ID
        #                     'debit': has_been_paid,
        #                     'amount_currency': 0,
        #                     'partner_id': False,
        #                 }))
        #
        #             for cc_obj in stored_obj.leih_admission_line_id:
        #                 ledger_id=611
        #                 try:
        #                     ledger_id = cc_obj.name.accounts_id.id
        #                 except:
        #                     ledger_id= 611 ## Diagnostic Income Head , If we don't assign any Ledger
        #
        #
        #
        #                 if context is None:
        #                     context = {}
        #
        #                 line_ids.append((0, 0, {
        #                     'analytic_account_id': False,
        #                     'tax_code_id': False,
        #                     'tax_amount': 0,
        #                     'name': cc_obj.name.name,
        #                     'currency_id': False,
        #                     'account_id': cc_obj.name.accounts_id.id,
        #                     'credit': cc_obj.total_amount,
        #                     'date_maturity': False,
        #                     'debit': 0,
        #                     'amount_currency': 0,
        #                     'partner_id': False,
        #                 }))
        #
        #
        #
        #
        #             jv_entry = self.pool.get('account.move')
        #
        #             j_vals = {'name': '/',
        #                       'journal_id': 2,  ## Sales Journal
        #                       'date': stored_obj.date,
        #                       'period_id': period_id,
        #                       'ref': stored_obj.name,
        #                       'line_id': line_ids
        #
        #                       }
        #
        #             saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
        #             if saved_jv_id > 0:
        #                 journal_id = saved_jv_id
        #                 try:
        #                     jv_entry.button_validate(cr,uid, [saved_jv_id], context)
        #                     journal_dict={'journal_id':journal_id,'general_admission_journal_relation_id':stored_obj.id}
        #                     journal_object.create(cr,uid,vals=journal_dict,context=context)
        #                 except:
        #                     import pdb
        #                     pdb.set_trace()
        #             return updated
        #             ### Ends the journal Entry Here
        #     else:
        updated = super(leih_hospital_admission, self).write(cr, uid, ids, vals, context=context)
        # raise osv.except_osv(_('Warning!'),
        #                      _("You cannot Edit the bill"))
        return updated

    @api.onchange('leih_admission_line_id', 'hospital_bed_line_id', 'hospital_bill_line_id', 'hospital_doctor_line_id')
    def onchange_admission_line(self):
        sumalltest = 0
        medicine_total = 0
        return_medicine_total = 0

        total_without_discount = 0
        for item in self.leih_admission_line_id:
            sumalltest = sumalltest + item.total_amount
            total_without_discount = total_without_discount + item.total_amount
        for item in self.hospital_bed_line_id:
            sumalltest = sumalltest + item.total_amount
            total_without_discount = total_without_discount + item.total_amount
        for item in self.hospital_bill_line_id:
            sumalltest = sumalltest + item.total_amount
            total_without_discount = total_without_discount + item.total_amount
        for item in self.hospital_doctor_line_id:
            sumalltest = sumalltest + item.total_amount
            total_without_discount = total_without_discount + item.total_amount

        self.total = sumalltest
        after_dis = (sumalltest * (self.doctors_discounts / 100))
        self.after_discount = 0

        self.grand_total = sumalltest + self.adjust_medicine_total
        self.due = sumalltest - self.paid - self.investigation_paid
        self.total_without_discount = total_without_discount

        return "X"

    @api.onchange('paid', 'investigation_paid')
    def onchange_paid(self):
        self.due = self.grand_total - (self.paid + self.investigation_paid)
        if self.payment_type:
            if self.payment_type.name == 'Visa Card':
                interest = self.payment_type.service_charge
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
        return 'x'

    @api.onchange('doctors_discounts')
    def onchange_doc_discount(self):
        discount = self.doctors_discounts
        for item in self.leih_admission_line_id:
            item.discount_percent = round((item.price * item.product_qty * discount) / 100)
            item.discount = discount
            item.total_discount = item.flat_discount + item.discount_percent
            item.total_amount = (item.price - item.total_discount) * item.product_qty

        #
        # aft_discount=(self.total*(self.doctors_discounts/100))
        # self.after_discount=aft_discount
        # self.grand_total = self.total - aft_discount - self.other_discount
        # self.due=self.total - aft_discount - self.other_discount- self.paid

        return "X"

    @api.onchange('other_discount')
    def onchange_other_discount(self):
        other_discount = self.other_discount
        total = self.total_without_discount
        gd = total - other_discount + self.adjust_medicine_total
        self.total = self.grand_total = gd
        self.due = self.grand_total - self.paid - self.investigation_paid
        return 'Nothing'

    # @api.onchange('other_discount')
    # def onchange_other_discount(self):
    #     other_discount = self.other_discount
    #     total = self.total_without_discount - other_discount
    #     line_total = 0
    #     for item in self.leih_admission_line_id:
    #         item.flat_discount = 0
    #         item.total_discount = item.discount_percent
    #         item.total_amount = item.price - item.total_discount
    #         line_total += item.total_amount
    #     if line_total < total:
    #         item.total_amount += total - line_total
    #         item.total_discount -= total - line_total
    #     elif line_total > total:
    #         item.total_amount -= line_total - total
    #         item.total_discount += line_total - total
    #     return 'Nothing'

    # self.grand_total = self.total - self.after_discount - self.other_discount
    # self.due=self.total - self.after_discount - self.other_discount- self.paid
    # return 'True'


class test_information(osv.osv):
    _name = 'hospital.admission.line'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('hospital.admission')
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rate = record.price
            discount = record.discount
            interst_amount = int(discount) * int(rate) / 100
            total_amount = int(rate) - interst_amount
            res[record.id] = total_amount
            # import pdb
            # pdb.set_trace()
        return res

    _columns = {

        'name': fields.many2one("examination.entry", "Item Name", ondelete='cascade'),
        'leih_admission_id': fields.many2one('hospital.admission', "Information"),
        'department': fields.char("Department"),
        'product_qty': fields.float("Quantity"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.float("Price"),
        'discount': fields.float("Discount"),
        'flat_discount': fields.integer("Flat Discount"),
        'total_discount': fields.integer("Total Discount"),
        'discount_percent': fields.integer("Discount Percent"),
        'total_amount': fields.float("Total Amount")

    }

    def onchange_test(self, cr, uid, ids, name, context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'department': dep_object.department.name, 'product_qty': 1, 'price': dep_object.rate,
               'total_amount': dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_discount(self, cr, uid, ids, name, discount, context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'total_amount': round(dep_object.rate - (dep_object.rate * discount / 100))}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    @api.onchange('product_qty')
    def onchange_qty(self):
        self.total_amount = self.price * self.product_qty


class admission_bill_register(osv.osv):
    _name = 'bill.register.general.admission.line'

    _columns = {
        'general_admission_line_id': fields.many2one('hospital.admission', 'admission'),
        'bill_id': fields.many2one("bill.register", "Bill ID"),
        'total': fields.float('Total')
    }

    def onchange_bill_id(self, cr, uid, ids, bill_id, context=None):
        lists = {'values': {}}
        dep_object = self.pool.get('bill.register').browse(cr, uid, bill_id, context=None)
        bill_info = {'total': dep_object.total}
        lists['value'] = bill_info
        return lists


class admission_payment_line(osv.osv):
    _name = 'general.admission.payment.line'

    _columns = {
        'admission_payment_line_id': fields.many2one('hospital.admission', 'admission payment'),
        'date': fields.datetime("Date"),
        'amount': fields.float('amount'),
        'type': fields.char('Type'),
        'card_no': fields.char('Card Number'),
        'bank_name': fields.char('Bank Name'),
        'money_receipt_id': fields.many2one('legh.money.receipt', 'Money Receipt ID'),

    }


class hospital_bed_line(osv.osv):
    _name = 'hospital.bed.line'

    _columns = {
        'hospital_bed_item_id': fields.many2one('hospital.admission', 'Bed Item'),
        'bed_no': fields.many2one('hospital.bed', "Bed Name", ondelete="cascade"),
        'ward_name': fields.char("Ward Name"),
        'start_date': fields.datetime("Start Date"),
        'end_date': fields.datetime("End Date"),
        'bed_qty': fields.float('Bed Quantity'),
        'perday_charge': fields.float('Per Day Charge'),
        'total_amount': fields.float("Total Amount"),
    }

    @api.onchange('bed_no')
    def onchange_bed(self):
        bed_obj = self.env['hospital.bed'].search([('id', '=', self.bed_no.id)])
        self.ward_name = bed_obj.ward_name
        self.bed_qty = 1
        self.perday_charge = bed_obj.perday_charge
        self.total_amount = bed_obj.perday_charge

    @api.onchange('bed_qty')
    def calculate_total(self):
        self.total_amount = self.perday_charge * self.bed_qty


class doctors_profile_line(osv.osv):
    _name = "doctor.profile.admission.line"

    _columns = {
        'name': fields.char("Name"),
        'doctor_profile_id': fields.many2one('doctors.profile', "Doctor Name"),
        'hospital_doctor_line_item': fields.many2one('hospital.admission', "Doctor Info"),
        'doctor_visit_qty': fields.float("Visit Times"),
        'visit_fee': fields.float("Visit Fee"),
        'total_amount': fields.float("Total Amount")

    }

    @api.onchange('doctor_profile_id')
    def onchange_doctor(self):
        doc_obj = self.env['doctors.profile'].search([('id', '=', self.doctor_profile_id.id)])
        self.doctor_visit_qty = 1
        self.visit_fee = doc_obj.ipd_visit
        self.total_amount = doc_obj.ipd_visit

    @api.onchange('visit_fee')
    def calculate_total_amount(self):
        self.total_amount = self.visit_fee

    @api.onchange('doctor_visit_qty')
    def calculate_total(self):
        self.total_amount = self.visit_fee * self.doctor_visit_qty


class hospital_medicine_line(osv.osv):
    _name = "hospital.medicine.line"

    _columns = {

        'product_name': fields.many2one('hospital.medicine', "Medicine Name"),
        'hospital_medicine_line_item': fields.many2one('hospital.admission', "Medicine Info"),
        'product_qty': fields.char('Product Quantity'),
        'unit_price': fields.char('Unit Price'),
        'total_price': fields.char("Total Price"),

    }


class hospital_bill_line(osv.osv):
    _name = "hospital.bill.line"

    _columns = {
        'name': fields.char("Name"),
        'hospital_admission_id': fields.many2one('hospital.admission', 'Hospital Admission'),
        'item_name': fields.many2one("examination.entry", "Item Name", ondelete='cascade'),
        'product_qty': fields.float('Product Quantity'),
        'bill_created_date': fields.datetime('Bill Created Date'),
        'delivery_date': fields.date("Delivery Date"),
        'department': fields.char("Department"),
        'date': fields.datetime("Date", readonly=True, default=lambda self: fields.datetime.now()),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount (%)"),
        'flat_discount': fields.integer("Flat Discount"),
        'total_discount': fields.integer("Total Discount"),
        'discount_percent': fields.integer("Discount Percent"),
        'total_amount': fields.integer("Total Amount")
    }

    def onchange_test(self, cr, uid, ids, name, context=None):
        tests = {'values': {}}
        # code for delivery date

        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        delivery_required_days = dep_object.required_time
        delivery_date = date.today() + timedelta(days=delivery_required_days)
        # import pdb
        # pdb.set_trace()
        abc = {'department': dep_object.department.name, 'price': dep_object.rate, 'total_amount': dep_object.rate,
               'bill_register_id.paid': dep_object.rate, 'delivery_date': delivery_date, 'product_qty': 1}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_discount(self, cr, uid, ids, price, discount, context=None):
        tests = {'values': {}}

        dis_amount = round(price - (price * discount / 100))

        abc = {'total_amount': dis_amount, 'total_discount': dis_amount}
        tests['value'] = abc

        return tests
