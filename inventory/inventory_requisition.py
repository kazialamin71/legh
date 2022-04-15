from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class inventory_requisition(osv.osv):
    _name = "inventory.requisition"

    _columns = {

        'name': fields.char("Inventory Requisition"),
        'reference_no':fields.char("Reference No"),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse Location',required=True),
        'partner_id': fields.many2one('res.partner', 'Receiver'),
        'challan_id': fields.many2one('stock.picking', 'Challan NO'),
        'expense_journal_id': fields.many2one('account.move', 'Expense Journal'),
        'department':fields.many2one("hr.department","Department",required=True),
        'inventory_requisition_line_ids':fields.one2many('inventory.requisition.line','inventory_requsition_id',string="Inventory Requision Items",required=True),
        'date':fields.date('Date'),
        'state': fields.selection(
            [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='pending', readonly=True)

    }
    _order = 'id desc'

    def confirm_transfer(self, cr, uid, ids, context=None):

        cc_ids = ids
        for id in cc_ids:
            ir_obj = self.browse(cr, uid, ids, context=context)
            if ir_obj.state == 'confirmed':
                raise osv.except_osv(_('Already Confirmed'), _('Sorry, it is already confirmed'))

            stock_picking_type_ids = self.pool['stock.picking.type'].search(cr, uid, [
                ('warehouse_id', '=', ir_obj.warehouse_id.id), ('code', '=', 'outgoing')],
                                                                            context=context)
            stock_picking_type_data = self.pool['stock.picking.type'].browse(cr, uid, stock_picking_type_ids,
                                                                             context=context)

            sorce_id = None
            dest_id = None
            picking_type_id = None


            for items in stock_picking_type_data:
                sorce_id = items.default_location_src_id.id
                dest_id = items.default_location_dest_id.id
                picking_type_id = items.id
            grn_vals = {
                'partner_id': ir_obj.partner_id.id,
                'date': fields.datetime.now(),
                'origin': ir_obj.name,
                'date_done' : fields.date.today(),
                'move_type': 'direct',
                'invoice_state': 'none',

                'picking_type_id': picking_type_id,
                # 'priority': 1, #Normal
            }
            ids = [id]

            move_line = []
            line_ids = []
            found_less_qty = False
            for items in ir_obj.inventory_requisition_line_ids:

                if items.quantity > items.product_name.qty_available:
                    found_less_qty = True
                    break
                move_line.append([0, False, {
                    'product_id': items.product_name.id,
                    'product_uom': 1,
                    'product_uom_qty': items.quantity,
                    'product_uos_qty': items.quantity,
                    'name': ir_obj.name,
                    'location_id': sorce_id,
                    'location_dest_id': dest_id,
                    'invoice_state': 'none',
                }])


            if found_less_qty == True:
                raise osv.except_osv(_('Warning!'),
                                     _('Stock is not available'))

            grn_vals['move_lines'] = move_line

            stock_picking_id = self.pool.get('stock.picking').create(cr, uid, grn_vals, context=context)



            picking_obj = self.pool.get('stock.picking')
            if stock_picking_id:
                picking_obj.action_confirm(cr, uid, [stock_picking_id], context=context)
                picking_obj.force_assign(cr, uid, [stock_picking_id], context=context)
                picking_obj.action_done(cr, uid, [stock_picking_id], context=context)



            ##### Create an Expense Journal ID ###################

            jv_entry = self.pool.get('account.move')

            if context is None: context = {}
            if context.get('period_id', False):
                return context.get('period_id')
            periods = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = periods and periods[0] or False
            line_ids =[]

            stock_picking_obj = self.pool['stock.picking'].browse(cr, uid, [stock_picking_id],
                                                                             context=context)[0]


            for items in stock_picking_obj.move_lines:
                inv_value=0
                for q_it in items.quant_ids:
                    inv_value = inv_value + q_it.inventory_value

                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': ir_obj.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': items.product_id.categ_id.property_account_expense_categ.id,  ### Cash ID
                    'debit': inv_value,
                    'amount_currency': 0,
                    'partner_id': False,
                }))
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': ir_obj.name,
                    'currency_id': False,
                    'credit': inv_value,
                    'date_maturity': False,
                    'account_id': items.product_id.categ_id.property_stock_account_output_categ.id,  ### Accounts Receivable ID
                    'debit': 0,
                    'amount_currency': 0,
                    'partner_id': False,
                }))



            j_vals = {'name': '/',
                      'journal_id': 2,  ## Sales Journal
                      'date':fields.date.today(),
                      'period_id': period_id,
                      'ref': ir_obj.name,
                      'line_id': line_ids

                      }

            saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)

            ################## Ends Here Expense Here ############

            confirm_cash_collection_query = "UPDATE inventory_requisition SET state='confirmed'," \
                                            "challan_id = {0}, expense_journal_id= {1} WHERE id={2}".format(
                stock_picking_id,saved_jv_id, id)
            cr.execute(confirm_cash_collection_query)
            cr.commit()

        return True

    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}

        stored = super(inventory_requisition, self).create(cr, uid, vals, context) # return ID int object


        if stored is not None:
            name_text = 'IR-0' + str(stored)
            cr.execute('update inventory_requisition set name=%s where id=%s', (name_text, stored))
            cr.commit()



        return stored


class inventory_requisition_line(osv.osv):
    _name="inventory.requisition.line"


    _columns = {
        'name':fields.char("Inventory Requisition Line Id"),
        'inventory_requsition_id':fields.many2one("inventory.requisition","Inventory Requision ID"),
        'product_name':fields.many2one('product.product','Product Name'),
        'available_qty':fields.float("available Qty",readonly=True),
        'quantity':fields.float("Quantity")
    }

    def onchange_product(self,cr,uid,ids,product_name,context=None):
        tests = {'values': {}}
        #code for delivery date

        dep_object = self.pool.get('product.product').browse(cr, uid, product_name, context=context)

        quantity_available=dep_object.qty_available
        # import pdb
        # pdb.set_trace()


        abc = {'available_qty':quantity_available}
        tests['value'] = abc
        return tests

