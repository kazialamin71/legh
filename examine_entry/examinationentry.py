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
        'code': fields.char("Item Code"),
        'name': fields.char("Item Name",required=True),
        # 'group':fields.many2one('diagnosis.group',"Group"),
        'department':fields.many2one("diagnosis.department",'Department'),
        'rate':fields.integer("Rate"),
        'tube_color':fields.selection([('red','Red'),('lavendar','Lavender'),('blue','Blue')],string="Tube Color"),
        'required_time':fields.integer("Required time(Days)"),
        'sample_req': fields.boolean("Sample Required"),
        'individual': fields.boolean("Individual"),
        'manual': fields.boolean("Manual"),
        ##for components
        'merge': fields.boolean("Merge"),
        'dependency': fields.boolean("Dependency"),
        'lab_not_required': fields.boolean("No Lab Required"),
        'indoor': fields.boolean("Indoor Item"),
        'sample_type':fields.many2one('sample.type','Sample Type'),
        'accounts_id':fields.many2one('account.account',"Account ID"),
        'examination_entry_line':fields.one2many('examination.entry.line','examination_id','Parameters'),
        'merge_ids':fields.many2many('examination.merge.line','merge_item_rel','item_id','merge_id',string="Merge"),
        'template_id' :fields.many2one('ir.actions.report.xml', string='Template')

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
        return super(examination_entry, self).create(cr, uid, vals, context=context)


        # import pdb
        # pdb.set_trace()
class testentryparamaerte(osv.osv):
    _name = 'examination.entry.line'
    _columns = {
        'name': fields.char("Name"),
        'sequence':fields.integer("Sequence"),
        'ref_value': fields.char(string="Ref. Value", store=False),
        'is_heading': fields.boolean(string="Is Heading"),
        'is_bold': fields.boolean(string="Is Bold"),
        'uom': fields.char(string='Unit of Measurement'),
        'examination_id': fields.many2one("examination.entry", "Examination Id"),
        'new_field1':fields.char(string="New Field 1"),
        'new_field2':fields.char(string="New Field 2"),
        'new_field3':fields.char(string="New Field 3"),
    }


class mergetestentryparamaerte(osv.osv):
    _name = 'examination.merge.line'
    _columns = {
        'merge_id': fields.many2many('examination.entry', "Test Entry"),
        'examinationentry_id': fields.many2one('examination.entry', "Merged Test Entry")

    }

