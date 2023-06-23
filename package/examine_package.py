from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class examine_package(osv.osv):
    _name = "examine.package"
    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name':fields.char("Package name"),
        'price': fields.float(string="Price"),
        'start_date': fields.date(string="Start Date"),
        'end_date': fields.date(string="End Date"),
        'active': fields.boolean("Active"),
        'examine_package_line_id':fields.one2many('examine.package.line', 'examine_package_id', 'Add test', required=True),
        'total': fields.float("Total")
    }


class examine_package_line(osv.osv):
    _name = 'examine.package.line'

    _columns = {

        'name': fields.many2one("examination.entry","Test Name", required=True, ondelete='cascade'),
        'examine_package_id': fields.many2one('examine.package', "Information"),
        'department': fields.char("Department"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
        'price': fields.integer("Price"),
        'discount': fields.integer("Discount"),
        'total_amount': fields.integer("Total Amount")

    }

    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'department':dep_object.department.name,'price': dep_object.rate,'total_amount':dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests




