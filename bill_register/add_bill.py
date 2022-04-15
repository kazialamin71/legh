from openerp.osv import fields, osv
from openerp import api
from openerp.tools.translate import _
from datetime import date, time

class add_bill(osv.osv):
    _name = "add.bill"


    def button_add_action(self,cr,uid,ids,context=None):

        admission_line=self.pool.get('legh.admission.line')
        admission_id=context.get("legh_admission_id")
        add_test_object=self.browse(cr,uid,ids,context=None)
        test_name=add_test_object.name.id
        test_price=add_test_object.price
        test_discount=add_test_object.discount
        test_amount=add_test_object.total_amount


        vals_dict = {'discount': test_discount, 'price': test_price, 'legh_admission_id': admission_id, 'name': test_name, 'total_amount': test_amount}
        # import pdb
        # pdb.set_trace()
        admission_id_confirm=admission_line.create(cr,uid,vals=vals_dict,context=None)
        #querying all details of paid,due,total

        query = "select total,grand_total,paid,after_discount,other_discount,due from legh_admission where id=%s"
        cr.execute(query, ([admission_id]))
        all_data = cr.dictfetchall()

        for item in all_data:
            total=item.get('total')
            grand_total = item.get('grand_total')
            paid_amount = item.get('paid')
            due_amount = item.get('due')
            after_discount = item.get('after_discount')
            other_discount = item.get('other_discount')


        # import pdb
        # pdb.set_trace()
        total=total+test_amount
        grand_total = total-(after_discount+other_discount)
        due_amount =grand_total-paid_amount
        cr.execute('update legh_admission set total=%s,grand_total=%s,due=%s where id=%s',
                   (total, grand_total, due_amount, admission_id))
        cr.commit()
        # import pdb
        # pdb.set_trace()





        return admission_id_confirm
        #


    _columns = {

        'name': fields.many2one("examination.entry", "Test Name", required=True, ondelete='cascade'),
        # 'bill_register_id': fields.many2one('bill.register', "Information"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount(%)"),
        'total_amount': fields.integer("Total Amount")

    }


    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'price': dep_object.rate,'total_amount':dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    @api.onchange('discount')
    def onchange_disocunt(self):
        if self.discount!=0:
            self.total_dis=(self.price*self.discount)/100
            self.total_amount=self.price-self.total_dis
        else:
            self.total_amount=self.price
        return 'X'
