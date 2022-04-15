from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class investigation_payment(osv.osv):
    _name = "investigation.payment"




    _columns = {

        'cal_st_date': fields.datetime('Calculation Start Date'),
        'cal_end_date': fields.datetime('Calculation End Date'),
        'ref_doctors': fields.many2one('doctors.profile', 'Doctor Name'),
        # 'total_payable_amount': fields.float('Total Payable Amount'),
        'investigation_payment_line_ids':fields.one2many('investigation.payment.line','investigation_payment_line_ids','Payment Line'),
        'given_discount_amount': fields.float('Total Discount'),
        'total_amount': fields.float('Total Payable Amount'),
        # 'total_patient': fields.float('Total Patients'),
        'total_bill': fields.float('Total Billing Amount'),
        'total_tests': fields.float('Total Tests in All Billing'),
        'paid_amount': fields.float('Paid Amount'),
        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('paid', 'Paid & Close'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)
    }

    @api.onchange('ref_doctors')
    def doctor_change(self):
        if self.ref_doctors:
            if self.cal_st_date == False or self.cal_end_date == False:
                raise osv.except_osv(_('Select'), _('Please select Start and End Date od Calculation'))

            st_date = self.cal_st_date
            end_date = self.cal_end_date
            commissioner_id = self.ref_doctors.id

            #fetching data of commission configuration
            comm_query = "select commission_configuration_line.test_id,commission_configuration_line.fixed_amount,commission_configuration_line.test_price,commission_configuration_line.applicable,commission_configuration_line.variance_amount,commission_configuration_line.est_commission_amount,commission_configuration_line.department_id,commission_configuration_line.max_commission_amount from commission_configuration,commission_configuration_line where commission_configuration.id= commission_configuration_line.commission_configuration_line_ids and commission_configuration_line.applicable = True and commission_configuration.doctor_id=%s"
            self._cr.execute(comm_query, ([commissioner_id]))

            comm_configuration_data = self._cr.dictfetchall()

            configured_test_ids = [items.get('test_id') for items in comm_configuration_data]


            #new code
#removed line: (bill_register_line.commission_paid = FALSE or bill_register_line.commission_paid is NULL)and

            query = "select bill_register_line.name,bill_register_line.total_amount,bill_register.ref_doctors from bill_register_line,bill_register where bill_register_line.bill_register_id=bill_register.id and bill_register_line.assign_doctors =%s and bill_register_line.name in %s and bill_register.date >=%s and bill_register.date <=%s"

            if len(configured_test_ids) > 0:

                self._cr.execute(query, (commissioner_id, tuple(configured_test_ids), st_date, end_date))

                all_data = self._cr.dictfetchall()
            else:
                all_data = []

            order_payment_line = list()

            total_amount = 0
            total_billing_amount = 0
            total_test_count = 0

            for bill_items in all_data:

                for c_items in comm_configuration_data:
                    if c_items.get('test_id') == bill_items.get('name') and c_items.get('applicable') == True:
                        total_test_count = total_test_count + 1

                        max_cap_amnt = c_items.get('max_amount')
                        fixed_amnt = c_items.get('fixed_amount')
                        var_amnt = c_items.get('variance_amount')
                        billed_amont = bill_items.get('total_amount')
                        total_billing_amount = total_billing_amount + billed_amont

                        cal_pay_amnt = 0

                        if var_amnt > 0.00:
                            cal_pay_amnt = round((billed_amont * (var_amnt / 100)), 2)

                        if fixed_amnt > 0.00:
                            cal_pay_amnt = round(fixed_amnt, 2)

                        if max_cap_amnt > 0.00:

                            if cal_pay_amnt > max_cap_amnt:
                                cal_pay_amnt = round(max_cap_amnt, 2)

                        order_payment_line.append({

                            'department_id': c_items.get('department_id'),
                            'name': bill_items.get('name'),
                            'discount_amount': bill_items.get('name'),
                            'test_amount': billed_amont,
                            'mou_payable_comm_var': var_amnt,
                            'mou_payable_comm_fixed': fixed_amnt,
                            'mou_payable_comm_max_cap': max_cap_amnt,
                            'payable_amount': cal_pay_amnt,

                        })
                        break

            self.investigation_payment_line_ids = order_payment_line
            self.total_amount = total_amount
            self.total_bill = total_billing_amount
            self.total_tests = total_test_count

        return "xXxXxXxXxX"

    @api.onchange('investigation_payment_line_ids')
    def payment_line_ids_code(self):
        total_sum = 0
        for line_item in self.investigation_payment_line_ids:
            total_sum = total_sum + line_item.payable_amount
        self.total_amount = total_sum
        return 'ss'






            #new code end



            ## Get all Commission Configuration List
            # and investigation_payment.cal_st_date <= st_date and investigation_payment.cal_end_date >= end_date


            # import pdb
            # pdb.set_trace()


            #comment out the section

        #     query = "select bill_register_id,name,department,total_amount from bill_register_line where assign_doctors=%s and date >= %s and date <= %s"
        #     self._cr.execute(query, (commissioner_id,st_date,end_date))
        #     all_data = self._cr.dictfetchall()
        #     # import pdb
        #     # pdb.set_trace()
        #
        #     investigation_payment_line = list()
        #
        #
        #     total_amount = 0
        #     # total_billing_amount = 0
        #     # total_test_count = 0
        #
        #     for bill_items in all_data:
        #
        #        #
        #        # import pdb
        #        # pdb.set_trace()
        #        bill_id=bill_items.get("bill_register_id")
        #        bill_register_obj=self.env['bill.register'].search([('id', '=', bill_id)])
        #        grand_total=bill_register_obj.grand_total
        #        # import pdb
        #        # pdb.set_trace()
        #        patient_name=bill_items.get("name")
        #        amount=bill_items.get("total_amount")
        #        total_amount = total_amount + bill_items.get("total_amount")
        #
        #        investigation_payment_line.append({
        #            'bill_id':bill_id,
        #            'patient_name':patient_name,
        #            'amount':amount,
        #            'after_discount_amount':grand_total
        #
        #
        #        })
        #
        #        # import pdb
        #        # pdb.set_trace()
        #
        #
        #     self.investigation_payment_line_ids = investigation_payment_line
        #     self.total_payable_amount = total_amount
        #
        # return "xXxXxXxXxX"
    #comment out end


    def investigation_pay(self, cr, uid, ids, context=None):
        cc_obj = self.browse(cr, uid, ids, context=context)
        for item in cc_obj.investigation_payment_line_ids:
            # import pdb
            # pdb.set_trace()

            item_id=item.investigation_booking_id
            query="update investigation_booking set payment_done=True where id=%s"
            cr.execute(query,([item_id]))
            cr.commit()
        return "XXXXX"



class investigation_payment_line(osv.osv):
        _name="investigation.payment.line"

        _columns = {
            'investigation_payment_line_ids':fields.many2one('investigation.payment','Admission Payment'),
            'department_id': fields.many2one("diagnosis.department", "Department"),
            'name': fields.many2one("examination.entry", "Test Name"),
            'discount_amount': fields.float('Discount Amount'),
            'test_amount': fields.float('Test Amount'),
            'mou_payable_comm_var': fields.float('MOU Payable Amount (%)'),
            'mou_payable_comm_fixed': fields.float('MOU Payable Fixed'),
            'mou_payable_comm_max_cap': fields.float('MOU Max CAP Amount'),
            'after_discount': fields.float('After Discount Amount'),
            'payable_amount': fields.float('Payable Amount'),
        }





