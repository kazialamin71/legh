from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class diagnosis_group(osv.osv):
    _name = "diagnosis.group"




    _columns = {

        'name': fields.char("Group Name",required=True),
        'department':fields.many2one('diagnosis.department',"Department"),
        'year':fields.integer("Year")

    }