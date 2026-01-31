# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    _columns = {
        'available_qty': fields.float(
            'Available Qty',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            readonly=True
        ),
    }

    def _compute_available_qty(self, cr, uid, product_id, picking_type_id, context=None):
        context = dict(context or {})
        qty = 0.0
        if product_id and picking_type_id:
            picktype = self.pool['stock.picking.type'].browse(cr, uid, picking_type_id, context=context)
            if picktype.default_location_dest_id:
                loc_id = picktype.default_location_dest_id.id
                prod = self.pool['product.product'].browse(cr, uid, product_id, context=dict(context, location=loc_id))
                qty = prod.qty_available  # use virtual_available if you want forecast
        return qty

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):

        res = super(purchase_order_line, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state, context=context
        )

        context = context or {}
        picking_type_id = context.get('picking_type_id')  # we will pass it from view context
        res.setdefault('value', {})
        res['value']['available_qty'] = self._compute_available_qty(cr, uid, product_id, picking_type_id, context=context)
        return res

    def onchange_product_qty(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
        # Optional: also refresh when qty changes (not required, but nice)
        res = super(purchase_order_line, self).onchange_product_qty(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state, context=context
        )
        context = context or {}
        picking_type_id = context.get('picking_type_id')
        res.setdefault('value', {})
        res['value']['available_qty'] = self._compute_available_qty(cr, uid, product_id, picking_type_id, context=context)
        return res
