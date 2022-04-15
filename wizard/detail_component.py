
import time
from openerp.osv import osv, fields


class cc_collection(osv.osv_memory):
    _name = 'detail.component'
    _description = 'Daily Opd Collection Report '

    _columns = {
        'date_start': fields.datetime('Date Start', required=True),
        'date_end': fields.datetime('Date End', required=True),
    }


    def print_detail_report(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end',], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]



        return self.pool['report'].get_action(cr, uid, [], 'legh.report_detail_component', data=datas, context=context)
