import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw


class optics_collcetion_details(report_sxw.rml_parse):

    def _get_user_names(self, t_dat=None, end_date=None):
        st_dat=t_dat
        end_date= end_date
        result = []

        query_for_optics="select optics_sale.name, optics_sale.total,legh_money_receipt.amount,legh_money_receipt.p_type from optics_sale,legh_money_receipt where legh_money_receipt.optics_sale_id=optics_sale.id and (legh_money_receipt.create_date <= '%s') and (legh_money_receipt.create_date >= '%s') group by optics_sale.name,optics_sale.total, legh_money_receipt.amount,legh_money_receipt.p_type order by optics_sale.name asc"
        self.cr.execute(query_for_optics % (end_date,st_dat))
        participant_ids = []
        opd_info = []
        for items in self.cr.fetchall():
            opd_info.append({
                'bill_id': items[0],
                'total_amount': items[1],
                'received_amount':items[2],
                'p_type': items[3],

            })
        # opd_info.append({'total':total_amount})

        return opd_info

    def _get_context_text(self, t_dat=None, end_date=None):
        txt = "Start Date " + str(t_dat)  + " End Date " + str(end_date)
        return txt

    def __init__(self, cr, uid, name, context):


        super(optics_collcetion_details, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_user_names': self._get_user_names,
            'get_user_context': self._get_context_text,
        })


class report_optics_collection(osv.AbstractModel):
    _name = 'report.legh.report_optics_collection'
    _inherit = 'report.abstract_report'
    _template = 'legh.report_optics_collection'
    _wrapped_report_class = optics_collcetion_details
