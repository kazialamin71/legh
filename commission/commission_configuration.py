# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class CommissionConfiguration(osv.osv):
    _name = "commission.configuration"
    _description = "Broker/Test/Department Commission Setup"
    _order = "id desc"

    def create(self, cr, uid, vals, context=None):
        record_id = super(CommissionConfiguration, self).create(cr, uid, vals, context=context)
        name = "CC-%04d" % record_id
        self.write(cr, uid, record_id, {'name': name}, context=context)
        return record_id

    def action_confirm(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids[0], context=context)

        if record.state == 'confirmed':
            raise UserError(_("Already confirmed"))

        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

        # Update doctor profile
        doctor_obj = self.pool.get('doctors.profile')
        doctor_obj.write(cr, uid, record.doctor_id.id, {'cc_id': record.id}, context=context)

        return True

    def action_cancel(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids[0], context=context)

        if record.state == 'confirmed':
            raise UserError(_("Cannot cancel confirmed configuration"))

        self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
        return True

    _columns = {
        'name': fields.char('Name', readonly=True),
        'doctor_id': fields.many2one("doctors.profile", "Broker/Doctor", required=True),
        'start_date': fields.date("MOU Start Date"),
        'end_date': fields.date("MOU End Date"),

        'department_line_ids': fields.one2many(
            "commission.department.line",
            "config_id",
            string="Department Commission Rules"
        ),

        'test_line_ids': fields.one2many(
            "commission.test.line",
            "config_id",
            string="Test Commission Rules"
        ),

        'state': fields.selection(
            [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status',
            readonly=True
        ),
    }

    _defaults = {
        'name': '/',
        'state': 'draft',
    }



class CommissionDepartmentLine(osv.osv):
    _name = "commission.department.line"
    _description = "Department-wise Commission Rule"

    _columns = {
        'config_id': fields.many2one(
            "commission.configuration",
            "Configuration",
            ondelete="cascade"
        ),

        'department_id': fields.many2one(
            "diagnosis.department",
            "Department",
            required=True
        ),

        'commission_type': fields.selection(
            [('fixed', 'Fixed Amount'), ('percent', 'Percentage')],
            'Type',
            required=True
        ),

        'commission_value': fields.float("Value", required=True),
    }



class CommissionTestLine(osv.osv):
    _name = "commission.test.line"
    _description = "Test-wise Commission Rule"

    _columns = {
        'config_id': fields.many2one(
            "commission.configuration",
            "Configuration",
            ondelete="cascade"
        ),

        'test_id': fields.many2one(
            "examination.entry",
            "Test",
            required=True
        ),

        'commission_type': fields.selection(
            [('fixed', 'Fixed Amount'), ('percent', 'Percentage')],
            'Type',
            required=True
        ),

        'commission_value': fields.float("Value", required=True),
    }



class DoctorsProfile(osv.osv):
    _inherit = "doctors.profile"

    _columns = {
        'cc_id': fields.many2one("commission.configuration", "Commission Rule"),
    }
