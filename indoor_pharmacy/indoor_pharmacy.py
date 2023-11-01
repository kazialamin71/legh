from openerp.osv import fields, osv
from openerp import api
from openerp.tools.translate import _
from datetime import date, time

class indoor_pos_order(osv.osv):
    _name = "indoor.pos.order"
    _description = "Point of Sale for Indoor"
    _order = "id desc"



    _columns = {
        'name': fields.char('Pres No.'),
        'date_order': fields.datetime('Order Date', readonly=True, select=True),
        'general_admission_id': fields.many2one('hospital.admission', 'General Admission ID',required=True),
        'patient_name': fields.many2one('patient.info', 'Patient Name',required=True),
        'amount_total': fields.float("Total"),
        'lines': fields.one2many('indoor.pos.order.line', 'order_id', 'Order Lines',required=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Price list', readonly=True),

        'state': fields.selection([('draft', 'New'),
                                   ('cancel', 'Cancelled'),
                                   ('confirm', 'Confirmed')],
                                  'Status', readonly=True),

        'account_move': fields.many2one('account.move', 'Journal Entry', readonly=True, copy=False),
        'picking_id': fields.many2one('stock.picking', 'Picking', readonly=True, copy=False),
        'note': fields.text('Internal Notes'),

        'prescription_item': fields.many2one('hospital.admission', "Medicine Info"),
        }

    _defaults = {
        'date_order': fields.datetime.now,
        'state': 'draft',
    }



    def create(self, cr, uid, vals, context=None):

        res =super(indoor_pos_order, self).create(cr, uid, vals, context)

        serial_no = 'PS-0'+str(res)

        #name_text = 'A-0' + str(stored)
        cr.execute('update indoor_pos_order set name=%s where id=%s', (serial_no, res))
        cr.commit()
        return res

    @api.onchange('general_admission_id')
    def onchange_general_admission_pharmacy(self):
        general_admission_obj = self.env['hospital.admission'].search([('id', '=', self.general_admission_id.id)])
        self.patient_name = general_admission_obj.patient_name

    @api.onchange('lines')
    def onchange_product(self):
        sumalltest = 0
        total_without_discount = 0
        for item in self.lines:
            sumalltest = sumalltest + item.total_amount

        self.amount_total = sumalltest

        return "X"
    def order_confirm(self, cr, uid, ids, context=None):

        self_obj = self.pool.get('indoor.pos.order').browse(cr, uid, ids, context=None)
        if self_obj.state == 'confirm':
            raise osv.except_osv(_('Warning!'),
                                 _('Already Confirmed Your Prescription'))

        stock_picking_type_ids = self.pool['stock.picking.type'].search(cr, uid, [
            ('warehouse_id', '=', 3), ('code', '=', 'outgoing')],
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
            'partner_id': 1,
            'date': fields.datetime.now(),
            'origin': self_obj.name,
            'date_done': fields.date.today(),
            'move_type': 'direct',
            'invoice_state': 'none',

            'picking_type_id': picking_type_id,
            # 'priority': 1, #Normal
        }
        ids = [id]

        move_line = []
        line_ids = []
        found_less_qty = False

        for items in self_obj.lines:

            if items.qty > items.product_id.qty_available:
                found_less_qty = True
                break
            move_line.append([0, False, {
                'product_id': items.product_id.id,
                'product_uom': 1,
                'product_uom_qty': items.qty,
                'product_uos_qty': items.qty,
                'name': self_obj.name,
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

        self_obj.picking_id = stock_picking_id

        general_admission_ids = self.pool.get("hospital.admission").search(cr, uid, [('id', '=', self_obj.general_admission_id.id)], context=None)
        general_admission_obj = self.pool.get('hospital.admission').browse(cr, uid, general_admission_ids, context=None)

        p_line_ids  = [itm.id for itm in general_admission_obj.prescription_id]
        p_line_ids.append(self_obj.id)
        general_admission_obj.prescription_id = p_line_ids


        self_obj.state = 'confirm'


class indoor_pos_order_line(osv.osv):
    _name = "indoor.pos.order.line"
    _description = "Lines of Indoor Point of Sale"
    _rec_name = "product_id"


    _columns = {
        'name': fields.char('Line No'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], required=True, change_default=True),
        'price_unit': fields.float(string='Unit Price'),
        'qty': fields.float('Quantity'),
        'total_amount': fields.float("Total"),
        'discount': fields.float('Discount (%)'),
        'available_qty': fields.float("available Qty", compute='_compute_qty'),
        'order_id': fields.many2one('indoor.pos.order', 'Order Ref', ondelete='cascade'),
        'create_date': fields.datetime('Creation Date', readonly=True),
    }

    @api.depends('product_id')
    def _compute_qty(self):
        for item in self:
            item.available_qty=item.product_id.qty_available
    def onchange_product(self, cr, uid, ids, name, context=None):
        products = {'values': {}}
        # code for delivery date

        product_object = self.pool.get('product.product').browse(cr, uid, name, context=None)

        abc = { 'qty': 1, 'price_unit': product_object.list_price,
               'total_amount': product_object.list_price}
        products['value'] = abc

        return products

    @api.onchange('qty')
    def onchange_qty(self):
        self.total_amount = self.price_unit * self.qty

    def onchange_discount(self, cr, uid, ids, price_unit, discount, context=None):
        tests = {'values': {}}

        dis_amount = round(price_unit - (price_unit * discount / 100))

        abc = {'total_amount': dis_amount}
        tests['value'] = abc

        return tests
