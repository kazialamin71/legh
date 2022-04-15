from openerp.osv import fields, osv
import datetime


class customReportWiz(osv.osv_memory):

    _name = 'custom.report.wiz'
    _description = 'Custom Report Wiz'

    _columns = {
        'date_from': fields.date("From Date"),
        'date_to': fields.date("TO Date"),

    }

    _defaults = {
        'date_from': datetime.datetime.today(),
        'date_to': datetime.datetime.today()
    }


    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}

        result = {
                'date_from': data['form']['date_from'],
                'date_to': data['form']['date_to']
                  }

        return result

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = {}

        data = self.read(cr, uid, ids, ['date_from', 'date_to'], context=context)[0]

        datas = {
            'ids': context.get('active_ids', []),
            'model': 'custom.report.wiz',
            'form': data
        }

        return {'type': 'ir.actions.report.xml',
                'report_name': 'custom.report.xls',
                'datas': datas
                }

