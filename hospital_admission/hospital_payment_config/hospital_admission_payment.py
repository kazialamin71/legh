from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api





class admission_payment(osv.osv):
    _name = "admission.payment.configuration"




    _columns = {

        'name': fields.char("Name"),
        'doctor_id': fields.many2one('doctors.profile', 'Doctor/Broker Name'),
        'start_date':fields.date('MOU Start Date'),
        'end_date':fields.date('MOU End Date'),
        'overall_admission_rate': fields.float('Overall admission Rate (%)'),
        'overall_default_discount': fields.float('Overall Discount Rate (%)'),
        'max_default_discount': fields.float('Max Discount Rate (%)'),
        'deduct_from_discount': fields.boolean("Deduct Excess Discount From admission"),
        'add_few_departments': fields.boolean("Add by Department"),
        'department_ids':fields.many2one('diagnosis.department','Department List'),
        'admission_configuration_line_ids':fields.one2many("admission.payment.configuration.line",'admission_configuration_line_ids',"admission Lines"),
        'state': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }

    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'

    @api.model
    def create(self, vals):
        record = super(admission_payment, self).create(vals)

        record.name = 'CA-0' + str(record.id)
        return record

    @api.onchange('overall_admission_rate')
    def add_tests_ids_in_line_with_rate(self):
        line_data =[]
        if self.overall_admission_rate:
            try:
                comm_rate = round((self.overall_admission_rate/100),2)
            except:
                comm_rate=0
            if self.admission_configuration_line_ids:
                for items in self.admission_configuration_line_ids:
                    est_comm = round((comm_rate*items.test_price),2)

                    line_data.append({

                        'department_id': items.department_id,
                        'test_id': items.test_id,
                        'applicable': items.applicable,
                        'fixed_amount': items.fixed_amount,
                        'variance_amount': comm_rate,
                        'test_price': items.test_price,
                        'est_admission_amount': est_comm,
                        'max_admission_amount': items.max_admission_amount

                    })
        self.admission_configuration_line_ids=line_data


        return 'x'


    @api.onchange('department_ids')
    def add_tests_ids_in_line(self):
        comm_rate=0
        if self.overall_admission_rate:
            try:
                comm_rate = round((self.overall_admission_rate / 100), 2)
            except:
                comm_rate=0
        if self.department_ids:
            depet_id=self.department_ids.id
            query="select id,name,department,rate from examination_entry where department=%s"
            self._cr.execute(query, ([depet_id]))
            all_data = self._cr.dictfetchall()
            configure_line=[]
            # import pdb
            # pdb.set_trace()


            if self.admission_configuration_line_ids:
                for items in self.admission_configuration_line_ids:
                    est_comm = round((comm_rate*items.test_price),2)

                    configure_line.append({

                        'department_id': items.department_id,
                        'test_id': items.test_id,
                        'applicable': items.applicable,
                        'fixed_amount': items.fixed_amount,
                        'variance_amount': comm_rate,
                        'test_price': items.test_price,
                        'est_admission_amount': est_comm,
                        'max_admission_amount': items.max_admission_amount

                    })


            for items in all_data:
                est_amnt=round((comm_rate*items.get('rate')),2)
                configure_line.append(
                    {

                        'department_id': items.get('department'),
                        'test_id': items.get('id'),
                        'applicable':True ,
                        'fixed_amount': 0,
                        'variance_amount':0 ,
                        'test_price': items.get('rate'),
                        'est_admission_amount': est_amnt,
                        'max_admission_amount': 0

                    }
                )
            self.admission_configuration_line_ids=configure_line



        return "xXxXxXxXxX"



    def confirm_configuration(self, cr, uid, ids, context=None):

        cr.execute("update admission_payment set state='done' where id=%s", (ids))
        cr.commit()

        config_data = self.browse(cr, uid, ids, context=context)
        doc_id = config_data.doctor_id.id

        if config_data.state == 'done':
            raise osv.except_osv(_('Already Confirmed!'),
                                 _('Already Confirmed'))


        cr.execute("update doctors_profile set cc_id=%s where id=%s", ([doc_id,ids[0]]))
        cr.commit()




        return True

    def cancel_configuration(self, cr, uid, ids, context=None):
        config_data = self.browse(cr, uid, ids, context=context)

        if config_data.state == 'done':
            raise osv.except_osv(_('Already Confirmed!'),
                                 _('Already Confirmed'))

        cr.execute("update admission_payment set state='cancelled' where id=%s", (ids))
        cr.commit()

        return True






class admission_payment_line(osv.osv):
    _name = "admission.payment.configuration.line"

    _columns = {
        'name':fields.char("name"),
        'admission_configuration_line_ids': fields.many2one('admission.payment.configuration', 'admission Configuration ID'),
        'department_id':fields.many2one('diagnosis.department','Department'),
        'test_id':fields.many2one('examination.entry','Test Name'),
        'applicable':fields.boolean('Applicable'),
        'fixed_amount': fields.float('Fixed Amount'),
        'variance_amount': fields.float('Amount (%)'),
        'test_price': fields.float('Test Fee'),
        'est_admission_amount': fields.float('admission Amount'),
        'max_admission_amount': fields.float('Max admission Amount'),


    }


# class doctors_profile(osv.osv):
#     _inherit = "doctors.profile"
#     _columns = {
#
#         'cc_id': fields.many2one('admission.payment', 'admission Rule')
#     }

