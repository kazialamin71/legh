from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class laundry(osv.osv):
    _name = "leih.expense"




    _columns = {
        'expense_type': fields.selection([('internal', 'Internal'), ('external', 'External'), ('convinent', 'Convinent'),('entertainment','Entertainment')],string="Expense Type"),
        'ex_name': fields.char("Expense Name"),
        'amount':fields.float('Amount',required=True),
        'responsible_person':fields.char('Responsible Person'),
        'date':fields.date('Date'),
        'description': fields.text("Description"),
        'state': fields.selection(
            [('pending', 'Pending'), ('approved', 'Approved'), ('canceled', 'Canceled')],
            'Status', default='pending', required=True, readonly=True, copy=False,
        )
        # 'nid':fields.integer("NID")

    }


    def approve_expense(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update leih_expense set state='approved' where id=%s", (ids))
            cr.commit()
        return True

    def cancel_expense(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update leih_expense set state='canceled' where id=%s", (ids))
            cr.commit()
        return True