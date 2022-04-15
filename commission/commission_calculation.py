from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time
from openerp import api

class commissioncalculation(osv.osv):
    _name = "commission.calculation"




    _columns = {

        'name': fields.char("Name"),
        'doctor_id': fields.many2one('doctors.profile', 'Doctor/Broker Name'),
        'start_date':fields.date('Calculation Start Date'),
        'end_date':fields.date('Calculation End Date'),
        'total_commission_amount': fields.float('Total Commission Amount'),
        'given_discount_amount': fields.float('Total Discount Amount'),
        'total_paybale_amount': fields.float('Total Payable Amount'),
        'no_of_total_patient': fields.float('Total Patients'),
        'no_of_total_bill': fields.float('Total Bill'),
        'no_of_total_bill_amount': fields.float('Total Bill Amount'),
        'no_of_total_test': fields.float('Total Test'),


        'commission_calculation_line_ids':fields.one2many("commission.calculation.line",'commission_calculation_line_ids',"Commission Lines"),
        'status': fields.selection(
            [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled'),('close', 'Closed'),],
            'Status', default='pending', readonly=True),
        'state': fields.selection(
            [('pending', 'Unpaid'), ('partially_paid', 'Partially Paid'), ('paid', 'Paid') ],
            'State', default='pending', readonly=True)

    }

    _defaults = {
        'status': 'pending',
        'state': 'pending',

    }

    _order = 'id desc'

class commissioncalculationline(osv.osv):
    _name = "commission.calculation.line"

    _columns = {
        'commission_calculation_line_ids': fields.many2one('commission.calculation', 'Commission calculation ID'),
        'department_id':fields.many2one('diagnosis.department','Department'),
        'test_id':fields.many2one('examination.entry','Test Name'),
        'discount_amount': fields.float('Discount Amount'),
        'test_amount': fields.float('Test Amount'),
        'mou_payable_commission_var': fields.float('MOU Payable Commission (%)'),
        'mou_payable_commission': fields.float('MOU Payable Commission Fixed'),
        'payble_amount': fields.float('Payable Amount'),
        'after_discount_amount': fields.float('After Discount Amount'),
        'mou_max_cap': fields.float('MOU Max Cap Amount'),
     


    }
