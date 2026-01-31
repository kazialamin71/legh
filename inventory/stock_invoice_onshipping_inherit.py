# -*- coding: utf-8 -*-
from openerp.osv import osv

class stock_invoice_onshipping(osv.osv_memory):
    _inherit = 'stock.invoice.onshipping'

    def create_invoice(self, cr, uid, ids, context=None):
        context = context or {}

        # active_id = current picking id (button clicked from stock.picking)
        picking_id = context.get('active_id')
        picking = picking_id and self.pool['stock.picking'].browse(cr, uid, picking_id, context=context) or False
   

        # get PO name
        po_name = False
        if picking:
            po_name = picking.origin or False
            if not po_name:
                # fallback: from purchase line
                for mv in picking.move_lines:
                    if mv.purchase_line_id and mv.purchase_line_id.order_id:
                        po_name = mv.purchase_line_id.order_id.name
                        break

        # call standard method (creates invoice)
        res = super(stock_invoice_onshipping, self).create_invoice(cr, uid, ids, context=context)

        # standard wizard usually returns an action with res_id (created invoice id)

        # write PO name to your custom field reference_type
        if res and po_name:
            self.pool['account.invoice'].write(cr, uid, res, {'supplier_invoice_number': po_name}, context=context)

        return res
