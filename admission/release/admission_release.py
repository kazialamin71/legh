from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class admission_release(osv.osv):
    _name = "admission.release"


    _columns = {

        'total':fields.float("Total"),
        'paid': fields.float("Paid"),
        'unpaid':fields.float("Unpaid"),
        'admission_id':fields.many2one("leih.admission", 'Admission'),
        'pay': fields.float("Pay"),
        'release_note':fields.text("Release Note")

    }


    def button_add_action(self, cr, uid, ids, context=None):
        values = {}
        state='released'
        try:
            stored_obj = self.browse(cr, uid, [ids[0]], context=context)
            admission_id = stored_obj.admission_id.id
            note = stored_obj.release_note

            cr.execute('update leih_admission set release_note=%s,state=%s where id=%s', (note,state, admission_id))
            cr.commit()
        except:
            pass
        # ## Bill Status Will Change



        return True
