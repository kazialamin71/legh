from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class inventory_product_entry(osv.osv):
    _name = "inventory.product.entry"


    _columns = {

        'name': fields.char("Entry No", readonly=True),
        'invoice_no':fields.char("Invoice No"),
        'reference_no':fields.char("Reference No"),
        'total':fields.float("Total Amount"),
        'partner_id':fields.many2one('res.partner','Employee Name',required=True),
        'grn_id':fields.many2one('stock.picking','GRN NO'),
        'grn_journal_id':fields.many2one('account.move','GRN Journal'),
        'advance_journal_id':fields.many2one('account.move','Advance Journal'),
        'department':fields.many2one("hr.department","Department"),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse Location',required=True),
        'inventory_product_entry_line_ids':fields.one2many('inventory.product.entry.line','inventory_product_entry_id',string="Inventory Requision Items",required=True),
        'date':fields.date('Date'),
        'state': fields.selection(
            [('pending', 'Pending'), ('confirmed', 'Receive Product'),('verify', 'Verified'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }
    _order = 'id desc'
    #calculating total
    @api.onchange('inventory_product_entry_line_ids')
    def onchange_product_line(self):
        sumallproduct = 0
        for item in self.inventory_product_entry_line_ids:
            sumallproduct = sumallproduct + item.total_price


        self.total = sumallproduct
        #

        return "X"



    def confirm_finance(self, cr, uid, ids, context=None):
        cc_ids = ids
        for id in cc_ids:
            ir_obj = self.browse(cr, uid, ids, context=context)
            line_ids=[]
            if ir_obj.state == 'verify':
                raise osv.except_osv(_('Already Verified'), _('Sorry, it is already verified'))

            if context is None: context = {}
            if context.get('period_id', False):
                return context.get('period_id')
            periods = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = periods and periods[0] or False

            if context is None:
                context = {}

            cc_obj = self.browse(cr, uid, ids, context=context)

            line_ids.append([0, False, {
                'name': cc_obj.name,
                'partner_id': cc_obj.partner_id.id,
                'account_id': cc_obj.partner_id.property_account_payable.id,
                'debit': cc_obj.total,
                'credit': 0,
            }])

            line_ids.append([0, False, {
                'name': cc_obj.name,
                'partner_id': cc_obj.partner_id.id,
                'account_id': 120, ## Advance Cash
                'debit': 0,
                'credit': cc_obj.total,
            }])


            j_vals = {'name': '/',
                      'journal_id': 6,  ## Advance Cash Journal
                      'date': fields.date.today(),
                      'period_id': period_id,
                      'ref': cc_obj.name,
                      'line_id': line_ids

                      }


            jv_entry = self.pool.get('account.move')

            saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
            if saved_jv_id > 0:
                journal_id = saved_jv_id
            jv_entry.button_validate(cr, uid, [saved_jv_id], context)

            ## Ends here

            confirm_cash_collection_query = "UPDATE inventory_product_entry SET state='verify'," \
                                            "advance_journal_id = {0}  WHERE id={1}".format(
                saved_jv_id, id)
            cr.execute(confirm_cash_collection_query)
            cr.commit()

        return True



    def confirm_transfer(self, cr, uid, ids, context=None):

        cc_ids = ids
        for id in cc_ids:
            ir_obj = self.browse(cr, uid, ids, context=context)
            if ir_obj.state == 'confirmed':
                raise osv.except_osv(_('Already Confirmed'), _('Sorry, it is already confirmed'))

            stock_picking_type_ids = self.pool['stock.picking.type'].search(cr, uid, [('warehouse_id', '=', ir_obj.warehouse_id.id),('code', '=', 'incoming')],
                                                                            context=context)
            stock_picking_type_data = self.pool['stock.picking.type'].browse(cr, uid, stock_picking_type_ids,
                                                                             context=context)

            sorce_id = None
            dest_id = None
            picking_type_id=None

            for items in stock_picking_type_data:
                sorce_id = items.default_location_src_id.id
                dest_id = items.default_location_dest_id.id
                picking_type_id = items.id
            grn_vals = {
                'partner_id': ir_obj.partner_id.id,
                'date': fields.datetime.now(),
                'origin': ir_obj.name,
                'move_type': 'one',
                'invoice_state': 'none',

                'picking_type_id': picking_type_id,
                # 'priority': 1, #Normal
            }
            ids = [id]


            move_line = []
            line_ids = []

            for items in ir_obj.inventory_product_entry_line_ids:

                move_line.append([0,False,{
                    'product_id':items.product_name.id,
                    'product_uom': 1,
                    'product_uom_qty':items.quantity,
                    'product_uos_qty': items.quantity,
                    'price_unit': items.unit_price,
                    'name':ir_obj.name,
                    'location_id':sorce_id,
                    'location_dest_id':dest_id,
                    'invoice_state':'none',
                }])

                line_ids.append([0, False, {
                    'name': ir_obj.name,
                    'partner_id': ir_obj.partner_id.id,
                    'account_id': items.account_id.id,
                    'debit': items.total_price,
                    'credit': 0,
                }])

            grn_vals['move_lines']=move_line

            grn_id = self.pool.get('stock.picking').create(cr, uid, grn_vals, context=context)

            stock_picking_id = grn_id
            stock_confirm = self.pool.get('stock.picking').action_confirm(cr, uid, [grn_id], context=context)

            stock_picking = self.pool.get('stock.picking').do_enter_transfer_details(cr, uid, [stock_picking_id],
                                                                                     context=context)

            trans_obj = self.pool.get('stock.transfer_details')
            trans_search = trans_obj.search(cr, uid, [('picking_id', '=', stock_picking_id)], context=context)

            trans_search = [trans_search[len(trans_search) - 1]] if len(trans_search) > 1 else trans_search

            trans_browse = self.pool.get('stock.transfer_details').browse(cr, uid, trans_search, context=context)

            trans_browse.do_detailed_transfer()
            # import pdb
            # pdb.set_trace()



            ### Start Journal Creation fro Here

            if context is None: context = {}
            if context.get('period_id', False):
                return context.get('period_id')
            periods = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = periods and periods[0] or False

            if context is None:
                context = {}


            cc_obj = self.browse(cr, uid, ids, context=context)



            line_ids.append([0, False, {
                'name': cc_obj.name,
                'partner_id': cc_obj.partner_id.id,
                'account_id': cc_obj.partner_id.property_account_payable.id,
                'debit': 0,
                'credit': cc_obj.total,
            }])

            j_vals = {'name': '/',
                      'journal_id': 6,  ## Advance Cash Journal
                      'date': fields.date.today(),
                      'period_id': period_id,
                      'ref': cc_obj.name,
                      'line_id': line_ids

                      }



            jv_entry = self.pool.get('account.move')

            saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
            if saved_jv_id > 0:
                journal_id = saved_jv_id
            jv_entry.button_validate(cr, uid, [saved_jv_id], context)

            ## Ends here

            confirm_cash_collection_query = "UPDATE inventory_product_entry SET state='confirmed'," \
                                            "grn_id = {0}, grn_journal_id={1} WHERE id={2}".format(
                grn_id,saved_jv_id, id)
            cr.execute(confirm_cash_collection_query)
            cr.commit()







        return True


    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}

        stored = super(inventory_product_entry, self).create(cr, uid, vals, context) # return ID int object


        if stored is not None:
            name_text = 'IPE-0' + str(stored)
            cr.execute('update inventory_product_entry set name=%s where id=%s', (name_text, stored))
            cr.commit()



        return stored


class inventory_product_entry_line(osv.osv):
    _name="inventory.product.entry.line"



    def _default_account(self):
        # XXX this gets the default account for the user's company,
        # it should get the default account for the invoice's company
        # however, the invoice's company does not reach this point
        if self._context.get('type') in ('out_invoice', 'out_refund'):
            return self.env['ir.property'].get('property_account_income_categ', 'product.category')
        else:
            return self.env['ir.property'].get('property_account_expense_categ', 'product.category')



    _columns = {
        'name':fields.char("Inventory Requisition Line Id"),
        'inventory_product_entry_id':fields.many2one("inventory.product.entry","Inventory Entry ID"),
        'product_name':fields.many2one('product.product','Product Name'),

        'account_id' : fields.many2one('account.account', string='Account',
                                     required=True, domain=[('type', 'not in', ['view', 'closed'])],
                                     default=_default_account,
                                     help="The income or expense account related to the selected product."),
        'quantity':fields.float("Quantity"),
        'unit_price':fields.float("Unit Price"),
        'total_price':fields.float("Total Price")
    }

    def onchange_product(self,cr,uid,ids,product_name,context=None):
        tests = {'values': {}}
        #code for delivery date

        dep_object = self.pool.get('product.product').browse(cr, uid, product_name, context=context)

        categ_id=dep_object.categ_id.id
        cat_object = self.pool.get('product.category').browse(cr, uid, categ_id, context=context)
        unit_price=dep_object.standard_price

        abc = {'account_id':cat_object.property_stock_account_input_categ,'unit_price':unit_price,'quantity':1,'total_price': unit_price}
        tests['value'] = abc
        return tests

    def onchange_quantity(self,cr,uid,ids,quantity,unit_price,context=None):
        tests = {'values': {}}
        # import pdb
        # pdb.set_trace()
        #code for delivery date
        total_amount=unit_price*quantity

        abc = {'total_price': total_amount}
        tests['value'] = abc
        return tests
    def onchange_unitprice(self,cr,uid,ids,unit_price,quantity,context=None):
        tests = {'values': {}}
        # import pdb
        # pdb.set_trace()
        #code for delivery date
        total_amount=unit_price*quantity

        abc = {'total_price': total_amount}
        tests['value'] = abc
        return tests
# class stock_picking(osv.osv):
#     _inherit = "stock.picking"
#
#     def create(self,cr, uid, vals, context=None):
#         import pdb
#         pdb.set_trace()







