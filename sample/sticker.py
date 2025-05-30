# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from datetime import datetime, timedelta

class sample(osv.osv):
    _name = "diagnosis.sticker"
    _order = 'id desc'


    def print_sticker(self,cr,uid,ids,context=None):
        statue='lab'

        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'lab' or report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is sample collected.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (statue, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'legh.report_sample_report', context=context)
        # return True

    def print_lab_report(self,cr,uid,ids,context=None):
        status='done'

        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()

        report_name=report_obj.test_id.template_id.report_name or 'legh.report_detail'

        return self.pool['report'].get_action(cr, uid, ids, report_name, context=context)
    def haematology_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'legh.report_haematology', context=context)

    #call the report for serology

    def serology_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'legh.report_serology', context=context)

    def microbiology_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'legh.report_microbiology', context=context)

    def biochemistry_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'legh.report_biochemistry', context=context)

    def urine_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'legh.report_urine', context=context)

    def stool_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'legh.report_stool', context=context)

    def capitalize_first_letter(self,text):
        """
        Capitalizes only the first letter of the given string.
        """
        if not text:
            return ''
        return text[0].upper() + text[1:]

    def add_six_hours(self,dt):
        if isinstance(dt, str):
            try:
                dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError("String must be in format 'YYYY-MM-DD HH:MM:SS'")
        elif not isinstance(dt, datetime):
            raise ValueError("Input must be a datetime string or datetime object")

        dt_no_seconds = dt.replace(second=0, microsecond=0)
        result = dt_no_seconds + timedelta(hours=6)
        return result

    def delivered(self,cr,uid,ids,context=None):
        status = 'delivered'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return True

    def set_to_lab(self,cr,uid,ids,context=None):
        status = 'lab'

        for id in ids:
            # report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return True

    _columns = {
        'name': fields.char('No #'),
        'full_name': fields.char('Name'),
        'bill_register_id':fields.many2one('bill.register','Bill register'),
        'admission_id':fields.many2one('legh.admission','Admission ID'),
        'department_id':fields.many2one('diagnosis.department','Department'),
        'doctor_id':fields.many2one('doctors.profile','Checked By'),
        'test_id':fields.many2one('examination.entry','Test Name'),
        'sticker_line_id':fields.one2many('diagnosis.sticker.line','sticker_id','Record Sample'),
        'state': fields.selection(
            [('cancel', 'Cancelled'), ('sample', 'Sample'), ('lab', 'Lab'),('done', 'Done'),('delivered','Delivered'),('indoor','Indoor')],
            'Status', required=True, readonly=True, copy=False,
            ),
        'antibiogram':fields.boolean("Antibiogram"),
        'has_growth':fields.boolean("Growth"),
        'growth_type': fields.selection([('profuse','Profuse'),('moderate','Moderate'),('scanty','Scanty')],string='Growth Type'),
        'bacteria':fields.char("Bacteria Name"),
        'hour':fields.char("Incubatig Hour"),
        'note':fields.selection(
            [('Culture Showed Profuse growth of Proteus species after incubating aerobically at 37&deg; for 72 hrs.', 'Showed Profused Growth of proteis species 37°- 72 hrs'), ('Custure has no growht of any pathogenic bacteria after incubating aerobically at 37&deg; for 72 hrs', 'No growth 37C- 72 hrs'), ('Culture showed growth of no Salmonella, Shigella bacteria after incubating aerobically at 37&deg; for 48 hrs.', 'growth of no salmonella, shigella- 37C-48 hrs')],'Status'),
        'comments':fields.char('Comments'),
        'advice':fields.char('Advice')

    }


class test_sample(osv.osv):
    _name = "diagnosis.sticker.line"

    _columns = {
        'test_name': fields.char("Name"),
        'sticker_id':fields.many2one('diagnosis.sticker','ID'),
        'result': fields.char('Result'),
        'uom': fields.char('Unit'),
        'ref_value': fields.text('Reference Value'),
        'bold':fields.boolean('Bold'),
        'group_by':fields.boolean('Group By'),
        'remarks': fields.char('Remarks'),
        'group':fields.char('Group')

    }




