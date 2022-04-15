from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time


class examination_entry(osv.osv):
    _name = "examination.entry"


    def onchange_manual(self, cr, uid, ids, manual=False, context=None):
        if manual:
            return {'value': {'boolean': True}}
        else:
            return {'value': {'boolean': False}}

    _columns = {

        'name': fields.char("Item Name",required=True),
        # 'group':fields.many2one('diagnosis.group',"Group"),
        'department':fields.many2one("diagnosis.department",'Department'),
        'rate':fields.integer("Rate"),
        'required_time':fields.integer("Required time(Days)"),
        'sample_req': fields.boolean("Sample Required"),
        'individual': fields.boolean("Individual"),
        'manual': fields.boolean("Manual"),
        'merge': fields.boolean("Merge"),
        'dependency': fields.boolean("Dependency"),
        'lab_not_required': fields.boolean("No Lab Required"),
        'indoor': fields.boolean("Indoor Item"),
        'sample_type':fields.many2one('sample.type','Sample Type'),
        'accounts_id':fields.many2one('account.account',"Account ID"),
        'examination_entry_line':fields.one2many('examination.entry.line','examinationentry_id','Parameters'),
        'merge_ids':fields.many2many('examination.merge.line','merge_item_rel','item_id','merge_id',string="Merge"),

    }
    def onchange_group(self,cr,uid,ids,group,context=None):

        test={'values':{}}
        dep_object=self.pool.get('diagnosis.group').browse(cr,uid,group,context=None)
        abc={'department':dep_object.department.name}
        test['value']=abc
        # import pdb
        # pdb.set_trace()
        return test


    def create(self, cr, uid, vals, context=None):

        if vals.get('sample_req'):
            sample=vals['sample_req']
        if vals.get('sample_type'):
            sample_type=vals.get('sample_type')
        if vals.get('examination_entry_line'):
            idss= vals['examination_entry_line']

        # import pdb
        # pdb.set_trace()
        # if sample==True:
        #     if sample_type:
        #         return super(examination_entry, self).create(cr, uid, vals, context=context)
        #     else:
        #         raise osv.except_osv(_('Warning!'), _('Sample type must defined.'))
        #
        #
        #
        # # if vals['manual']==True and idss or sample:
        # #     raise osv.except_osv(_('Warning!'), _('test name shouldnt exist.'))
        # # elif vals['manual']==False and not idss:
        # #     for names in examination_entry_line
        # else:
        return super(examination_entry, self).create(cr, uid, vals, context=context)


        # import pdb
        # pdb.set_trace()







# many2one('leih.doctors',"Test Names", required=True, ondelete='cascade', select=True)

class testentryparamaerte(osv.osv):
    _name = 'examination.entry.line'
    _columns = {

        'name': fields.char("Name",ondelete='cascade'),
        'examinationentry_id': fields.many2one('examination.entry', "Test Entry"),
        'reference_value': fields.char("Reference Value"),
        'bold':fields.boolean('Bold'),
        'group_by':fields.boolean("Group By"),
        'others': fields.char("Others")
    }


class mergetestentryparamaerte(osv.osv):
    _name = 'examination.merge.line'
    _columns = {
        'merge_id': fields.many2many('examination.entry', "Test Entry"),
        'examinationentry_id': fields.many2one('examination.entry', "Merged Test Entry")

    }

