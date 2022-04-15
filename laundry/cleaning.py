from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class laundry_clean(osv.osv):
    _name = "laundry.clean"




    _columns = {

        'name': fields.char("Name",required=True),
        'send_date':fields.date("Send Date"),
        'laundry_name':fields.many2one('laundry.laundry',"Laundry Name",required=True),
        'back_date': fields.date("Delivered Date"),
        'state': fields.selection(
            [('store', 'Store'), ('sent to laundry', 'Sent to Laundry'), ('received', 'Received'),
             ('cancelled', 'Cancelled')],
            'Status', default='sent to laundry', required=True, readonly=True, copy=False,
        ),
        'product_line':fields.one2many("laundry.clean.line","laundry_clean_id","Clean Product List")
        # 'nid':fields.integer("NID")


    }

    def receive(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update laundry_clean set state='received' where id=%s", (ids))
            cr.commit()
        return True

    def cancel_clean(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update legh_expense set state='cancelled' where id=%s", (ids))
            cr.commit()
        return True

class clean_line(osv.osv):
    _name = 'laundry.clean.line'


    _columns = {

        'laundry_clean_id': fields.many2one('laundry.clean', "Clean"),
        'linen_item': fields.many2one("laundry.product","Linen Item"),
        'quantity': fields.integer("Quantity"),
        'color': fields.char("Color"),
    }




class laundry_receive(osv.osv):
    _name = "laundry.receive"




    _columns = {

        'laundry_name': fields.many2one('laundry.laundry', "Laundry Name", required=True),
        'name': fields.char("Cloth Type",required=True),
        'color':fields.char('Color',required=True),
        'quantity':fields.integer('Quantity',required=True),
        'receive_date':fields.date("Receive Date"),

        # 'nid':fields.integer("NID")


    }