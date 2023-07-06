from openerp.osv import fields, osv
from openerp import api


class brokers_info(osv.osv):
    _name = "brokers.info"
    _rec_name = 'broker_name'

    _columns = {

        'broker_id': fields.char(string="Broker ID", readonly=True),
        'broker_name': fields.char("Broker Name", required=True),
        'status': fields.selection([('active', 'Active'), ('inactive', 'Inactive')], string='Status', default='active'),
        'commission_rate': fields.float("Commission Rate (%) "),
        'last_commission_calculation_date': fields.date("Last Commission Calculation Date"),
        'bill_info': fields.one2many("bill.register", 'referral', "Bill Register"),
        'doctor_ids': fields.many2many('doctors.profile', 'referral_relation', 'broker_id', 'doctor_id', "Broker Name"),

        # 'admission_info': fields.many2one("leih.admission", 'reffered_to_hospital', "Admission Info"),
        # 'commission': fields.many2one("commission", 'referral', "Commission"),
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        record = super(brokers_info, self).create(cr, uid, vals, context)
        if record is not None:
            name_text = 'BR-1001' + str(record)
            cr.execute('update brokers_info set broker_id=%s where id=%s', (name_text, record))
            cr.commit()
        return record

    #
    # def name_get(self, cr, uid, ids, context=None):
    #     if not ids:
    #         return []
    #     res = []
    #     for elmt in self.browse(cr, uid, ids, context=context):
    #         broker_name = elmt.broker_name
    #         try:
    #             broker_name = broker_name + ' ' + str(elmt.broker_id) if elmt.broker_id is not False else '---'
    #             res.append((elmt.id, broker_name))
    #         except ValueError:
    #             pass
    #     return res