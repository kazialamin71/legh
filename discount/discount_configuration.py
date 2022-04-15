from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class discount_configuration(osv.osv):
    _name = "discount.configuration"
    # _rec_name = 'patient_id'


    _columns = {

        'name': fields.char("Client Name"),
        'type': fields.selection([('fixed', 'Fixed'),('variance', 'Variance')], 'Type'),
        'overall_discount': fields.float("Overall Discount Amount(%)"),
        'department':fields.many2one("diagnosis.department","Department"),
        'from_date':fields.date("From (Date)"),
        'to_date':fields.date("To (Date)"),
        'discount_donfiguration_line_ids':fields.one2many('discount.configuration.line','discount_donfiguration_line_ids','All Tests')

    }

    @api.model
    def create(self, vals):
        record = super(discount_configuration, self).create(vals)
        return record

    # @api.onchange('overall_commission_rate')
    # def add_tests_ids_in_line_with_rate(self):
    #     line_data =[]
    #     if self.overall_commission_rate:
    #         try:
    #             comm_rate = round((self.overall_commission_rate/100),2)
    #         except:
    #             comm_rate=0
    #         if self.commission_configuration_line_ids:
    #             for items in self.commission_configuration_line_ids:
    #                 est_comm = round((comm_rate*items.test_price),2)
    #
    #                 line_data.append({
    #
    #                     'department_id': items.department_id,
    #                     'test_id': items.test_id,
    #                     'applicable': items.applicable,
    #                     'fixed_amount': items.fixed_amount,
    #                     'variance_amount': comm_rate,
    #                     'test_price': items.test_price,
    #                     'est_commission_amount': est_comm,
    #                     'max_commission_amount': items.max_commission_amount
    #
    #                 })
    #     self.commission_configuration_line_ids=line_data
    #
    #
    #     return 'x'


    @api.onchange('overall_discount')
    def onchange_overall_discount(self):
        line_data=[]
        if self.overall_discount:
            try:
                discount_rate=round((self.overall_discount/100),2)
            except:
                discount_rate=0



            query = "select id,name,rate,department from examination_entry"

            self._cr.execute(query)

            all_data = self._cr.dictfetchall()

            discount_configuration_line_ids = list()


            for items in all_data:
                est_discount = round((discount_rate * items.get('rate')), 2)

                discount_configuration_line_ids.append({

                    'test_id': items.get('id'),
                    'test_price': items.get('rate'),
                    'department_id': items.get('department'),
                    'variance_amount':self.overall_discount,
                    'after_discount':est_discount
                })

            self.discount_donfiguration_line_ids = discount_configuration_line_ids


            return "xXxXxXxXxX"


class discount_configuration_line(osv.osv):
    _name = "discount.configuration.line"
    _columns = {
        'discount_donfiguration_line_ids':fields.many2one('discount.configuration','Discount configuration Id'),
        'department_id':fields.many2one("diagnosis.department","Department"),
        'test_id':fields.many2one('examination.entry','Test Name'),
        'test_price':fields.float('Test Fee'),
        'applicable':fields.boolean("Applicable"),
        'fixed_amount': fields.float('Fixed Amount'),
        'variance_amount': fields.float('Amount (%)'),
        'after_discount': fields.float('After Discount Amount')

    }

