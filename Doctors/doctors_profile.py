from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class doctors_profile(osv.osv):
    _name = "doctors.profile"

    _columns = {

        'name': fields.char("Doctor Name",required=True),
        'doctor_id': fields.char("Doctor ID"),
        'department':fields.char('Department'),
        'designation':fields.char('Designation'),
        'degree':fields.char('Degree'),
        'institute':fields.char("Institute"),
        'type': fields.selection([('inhouse', 'In house'), ('consoled', 'Consoled'),('prttime','Part Time'),('outsid','Out Side')], string='Type', default='inhouse'),
        'status': fields.selection([('active', 'Active'), ('inactive', 'Inactive')], string='Status', default='active'),
        'others': fields.char("Others"),
        'bill_info':fields.one2many("bill.register",'ref_doctors',"Bill Register"),
        'admission_info':fields.many2one("legh.admission",'ref_doctors',"Admission Info"),
        'commission':fields.many2one("commission",'ref_doctors',"Commission"),
        'ipd_visit': fields.float("IPD Visit Fee"),

        'commission_rate':fields.float("Commission Rate (%) "),
        'last_commission_calculation_date':fields.date("Last Commission Calculation Date")
        # 'nid':fields.integer("NID")


    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        record = super(doctors_profile, self).create(cr, uid, vals, context)
        if record is not None:
            name_text = 'D-00' + str(record)
            cr.execute('update doctors_profile set doctor_id=%s where id=%s', (name_text, record))
            cr.commit()
        return record