from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class commission(osv.osv):
    _name = "commission"


    _columns = {

        'name': fields.char("Commission Calculation"),
        'ref_doctors': fields.many2one('doctors.profile', 'Doctor/Broker Name'),
        'commission_configuration_id': fields.many2one('commission.configuration', 'Commission Rule'),
        'commission_rate': fields.float('Commission Rate'),
        'cal_st_date': fields.date("Calculation Start Date", required=True),
        'cal_end_date': fields.date("Calculation End Date", required=True),
        'total_amount': fields.float('Total Commission Amount'),
        'given_discount_amount': fields.float('Total Discount'),
        'total_payable_amount': fields.float('Total Payable Amount'),
        'total_patient': fields.float('Total Patients'),
        'total_bill': fields.float('Total Billing Amount'),
        'total_tests': fields.float('Total Tests in All Billing'),
        'paid_amount': fields.float('Paid Amount'),
        'commission_line_ids':fields.one2many("commission.line",'commission_line_ids',"Commission Lines"),
        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'),('paid', 'Paid & Close'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }

    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'



    def btn_pay_bill(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih','commission_payment_form_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)


        return {
            'name': _("Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'commission.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_cc_id': ids[0],
                'default_doctor_id': inv.ref_doctors.id,
                'default_paid_amount': inv.total_payable_amount
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    def confirm_commission(self, cr, uid, ids, context=None):


        if ids is not None:
            cr.execute("update commission set state='done' where id=%s", (ids))
            cr.commit()

        return 'True'

    def cancel_commission(self, cr, uid, ids, context=None):

        if ids is not None:
            cr.execute("update commission set state='cancelled' where id=%s", (ids))
            cr.commit()

        return 'True'


    @api.model
    def create(self, vals):
        record = super(commission, self).create(vals)

        record.name = 'Com-0'+ str(record.id)
        return record

    @api.onchange('ref_doctors')
    def customer_on_select(self):



        if self.ref_doctors:
            if self.cal_st_date == False or self.cal_end_date == False:
                raise osv.except_osv(_('Select'), _('Please select Start and End Date od Calculation'))

            st_date = self.cal_st_date
            end_date = self.cal_end_date
            commissioner_id=self.ref_doctors.id
            commission_rate = 0
            c_query = "select commission_rate from doctors_profile where id=%s"
            self._cr.execute(c_query, ([commissioner_id]))
            com_data=self._cr.dictfetchall()
            for itm in com_data:
                commission_rate_raw = itm.get('commission_rate')
                break
            try:
                commission_rate = round((commission_rate_raw/100),2)
            except:
                commission_rate=0


            ## Get all Commission Configuration List

            comm_query = "select commission_configuration_line.test_id,commission_configuration_line.fixed_amount,commission_configuration_line.test_price,commission_configuration_line.applicable,commission_configuration_line.variance_amount,commission_configuration_line.est_commission_amount,commission_configuration_line.department_id,commission_configuration_line.max_commission_amount from commission_configuration,commission_configuration_line where commission_configuration.id= commission_configuration_line.commission_configuration_line_ids and commission_configuration_line.applicable = True and commission_configuration.doctor_id=%s"
            self._cr.execute(comm_query, ([commissioner_id]))

            comm_configuration_data = self._cr.dictfetchall()


            configured_test_ids = [items.get('test_id') for items in comm_configuration_data]

            ## Ends Here

            query = "select bill_register_line.name,bill_register_line.total_amount,bill_register.ref_doctors from bill_register_line,bill_register where bill_register_line.bill_register_id=bill_register.id and (bill_register_line.commission_paid = FALSE or bill_register_line.commission_paid is NULL)and bill_register.ref_doctors =%s and bill_register_line.name in %s and bill_register.date >=%s and bill_register.date <=%s"


            if len(configured_test_ids)>0:

                self._cr.execute(query, (commissioner_id,tuple(configured_test_ids),st_date,end_date))

                all_data = self._cr.dictfetchall()
            else:
                all_data=[]



            order_payment_line = list()

            total_amount = 0
            total_billing_amount=0
            total_test_count = 0


            for bill_items in all_data:

                for c_items in comm_configuration_data:
                    if c_items.get('test_id') == bill_items.get('name') and c_items.get('applicable') == True:
                        total_test_count = total_test_count + 1

                        max_cap_amnt = c_items.get('max_commission_amount')
                        fixed_amnt = c_items.get('fixed_amount')
                        var_amnt = c_items.get('variance_amount')
                        billed_amont = bill_items.get('total_amount')
                        total_billing_amount = total_billing_amount + billed_amont

                        cal_pay_amnt = 0

                        if var_amnt > 0.00:
                            cal_pay_amnt = round((billed_amont *(var_amnt/100)),2)

                        if fixed_amnt > 0.00:
                            cal_pay_amnt = round(fixed_amnt,2)




                        if max_cap_amnt > 0.00:

                            if cal_pay_amnt > max_cap_amnt:
                                cal_pay_amnt = round(max_cap_amnt,2)


                        order_payment_line.append({


                            'department_id': c_items.get('department_id'),
                            'name': bill_items.get('name'),
                            'discount_amount': bill_items.get('name'),
                            'test_amount': billed_amont,
                            'mou_payable_comm_var': var_amnt,
                            'mou_payable_comm_fixed': fixed_amnt,
                            'mou_payable_comm_max_cap': max_cap_amnt,
                            'payable_amount':cal_pay_amnt,

                        })
                        break

            self.commission_line_ids = order_payment_line
            self.total_amount=total_amount
            self.commission_rate=commission_rate_raw
            self.total_bill=total_billing_amount
            self.total_tests=total_test_count

        return "xXxXxXxXxX"

    @api.onchange('commission_line_ids')
    def commission_line_ids_code(self):
        total_sum = 0
        for line_item in self.commission_line_ids:
            total_sum = total_sum + line_item.payable_amount
        self.total_amount = total_sum
        return 'ss'


class commission_line(osv.osv):
    _name = "commission.line"

    _columns = {
        'commission_line_ids': fields.many2one('commission', 'commission'),
        'department_id': fields.many2one("diagnosis.department", "Department"),
        'name': fields.many2one("examination.entry", "Test Name"),
        'discount_amount': fields.float('Discount Amount'),
        'test_amount': fields.float('Test Amount'),
        'mou_payable_comm_var': fields.float('MOU Payable Commission Amount (%)'),
        'mou_payable_comm_fixed': fields.float('MOU Payable Commission Fixed'),
        'mou_payable_comm_max_cap': fields.float('MOU Max CAP Amount'),
        'after_discount': fields.float('After Discount Amount'),
        'payable_amount': fields.float('Payable Amount'),


        'bill_line_id': fields.many2one("bill.register.line",'Bill Register Line ID'),
    }

    @api.onchange('commission_rate')
    def commission_rate_change(self):
        try:
            if self.commission_rate:
                self.payable_amount = round((self.amount * round((self.commission_rate/100),2)),2)
            else:
                self.payable_amount = 0
        except:
            self.payable_amount=0

        return 'xxx'
