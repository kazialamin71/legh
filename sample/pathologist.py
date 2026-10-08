# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _


class pathologist_info(osv.osv):
    _name = "pathologist.info"
    _description = "Pathologist (Report Signatory)"
    _order = 'is_default desc, name'

    _columns = {
        'name': fields.char('Doctor Name', required=True),
        'degree': fields.char('Degrees', help='e.g. MBBS, MPhil (Pathology)'),
        'designation': fields.char('Designation', help='e.g. Asst. Professor & Head of Dept.'),
        'is_default': fields.boolean('Default', help='This doctor will be printed on pathology reports.'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'is_default': False,
        'active': True,
    }

    # ------------------------------------------------------------
    # Keep only ONE default pathologist
    # ------------------------------------------------------------
    def _unset_other_defaults(self, cr, uid, keep_ids, context=None):
        other_ids = self.search(cr, uid, [('is_default', '=', True), ('id', 'not in', keep_ids)], context=context)
        if other_ids:
            super(pathologist_info, self).write(cr, uid, other_ids, {'is_default': False}, context=context)
        return True

    def create(self, cr, uid, vals, context=None):
        new_id = super(pathologist_info, self).create(cr, uid, vals, context=context)
        if vals.get('is_default'):
            self._unset_other_defaults(cr, uid, [new_id], context=context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if vals.get('is_default') and len(ids) > 1:
            raise osv.except_osv(_('Warning!'), _('Only one pathologist can be set as default.'))
        res = super(pathologist_info, self).write(cr, uid, ids, vals, context=context)
        if vals.get('is_default'):
            self._unset_other_defaults(cr, uid, ids, context=context)
        return res

    # ------------------------------------------------------------
    # Default pathologist must be active
    # ------------------------------------------------------------
    def _check_default_active(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.is_default and not rec.active:
                return False
        return True

    _constraints = [
        (_check_default_active, 'The default pathologist must be active.', ['is_default', 'active']),
    ]