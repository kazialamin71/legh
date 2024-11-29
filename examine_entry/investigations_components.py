from openerp import api
from openerp.exceptions import ValidationError
from openerp.osv import fields, osv
from datetime import date, time, timedelta, datetime


class InvestigationComponents(osv.osv):
    _name = "investigation.components"
    _order = 'id desc'



    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name': fields.char("Name"),
        'ref_value': fields.char(string="Ref. Value", store=False),
        'is_heading':fields.boolean(string="Is Heading"),
        'is_bold': fields.boolean(string="Is Bold"),
        'uom' : fields.selection([
        ('ml', 'Milliliters (mL)'),
        ('l', 'Liters (L)'),
        ('g', 'Grams (g)'),
        ('g_dl', 'Grams per Deciliter (g/dL)'),
        ('g_l', 'Grams per Liter (g/L)'),
        ('iu_l', 'International Units per Liter (IU/L)'),
        ('iu_ml', 'International Units per Milliliter (IU/mL)'),
        ('mcg', 'Micrograms (mcg)'),
        ('mcg_dl', 'Micrograms per Deciliter (mcg/dL)')
    ], string='Unit of Measurement', required=True),
        'examination_id':fields.many2one("examination.entry","Examination Id")




    }
