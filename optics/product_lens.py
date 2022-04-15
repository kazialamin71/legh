from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class product_lens(osv.osv):
    _name = "product.lens"

    _columns = {
        'lens_code':fields.char("Code"),
        'name':fields.char("Name"),
        'purchase_price':fields.float("Purchase price"),
        'sell_price':fields.float("Sale Price"),
        'lens_type':fields.selection([('glass','Glass'),('plastic','Plastic')],default='plastic'),
        'supplier':fields.char("Supplier Name"),
    }

