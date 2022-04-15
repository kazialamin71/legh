from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class money_receipt(osv.osv):
    _name = "leih.money.receipt"


    _columns = {
        'name':fields.char("MR ID"),
        'date':fields.date("Date"),
        'bill_id':fields.many2one("bill.register","BIll ID"),
        'admission_id':fields.many2one("leih.admission","Admission ID"),
        'optics_sale_id':fields.many2one("optics.sale","Optics Sale ID"),
        'amount':fields.float("Paid Amount"),
        'bill_total_amount':fields.float("Total Amount"),
        'due_amount':fields.float("Due Amount"),
        'p_type':fields.selection([
            ('advance', 'Advance'),
            ('due_payment', 'Due Payment')], 'Payment Method'),
        'already_collected':fields.boolean("Collected", default=False),
        'diagonostic_bill':fields.boolean("Diagonstic Bill"),
        'type':fields.many2one("payment.type","Type"),
        'user_id':fields.many2one('res.users','Current User', default=lambda self: self.env.user.id),
        'state': fields.selection([
            ('confirm', 'confirm'),
            ('cancel', 'Cancelled')], 'State', default='confirm'),
    }


    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        res = super(money_receipt, self).create(cr, uid, vals, context)
          ## Update Bill regiester Paid Value

        # try:
        #     paid_amount=0
        #     bill_id = [vals.get('bill_id')]
        #     abc = self.pool.get('bill.register').browse(cr, uid, bill_id, context=context)[0]
        #     paid_amount = abc.paid + float(vals.get('amount'))
        #     cr.execute("update bill_register set paid=%s where id=%s", ([paid_amount,bill_id]))
        #     cr.commit()
        # except:
        #     pass


        return res
