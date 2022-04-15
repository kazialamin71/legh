import datetime
from datetime import timedelta
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw


class detail_collcetion_details(report_sxw.rml_parse):

    def _get_user_names(self, t_dat=None, end_date=None):
        st_dat=t_dat
        end_date= end_date
        result = []

        opd_component_q = "select sum(opd_ticket_line.total_amount) as t_amnt,count(opd_ticket_line.total_amount) as t_count, opd_ticket_line.price," \
                          "(select opd_ticket_entry.name from opd_ticket_entry where opd_ticket_entry.id=opd_ticket_line.name) as name ,opd_ticket_line.department " \
                          "from opd_ticket_line,opd_ticket where opd_ticket_line.opd_ticket_id=opd_ticket.id and (opd_ticket.create_date <= '%s')" \
                          " and (opd_ticket.create_date >= '%s') and opd_ticket.state='confirmed' " \
                          "group by opd_ticket_line.name, opd_ticket_line.department,opd_ticket_line.price order by opd_ticket_line.price desc"

        bill_q = "select sum(bill_register_line.total_amount),count(bill_register_line.total_amount) as tl," \
                 " (select examination_entry.name from examination_entry where examination_entry.id=bill_register_line.name) as name,bill_register_line.department,(select sum(legh_money_receipt.bill_total_amount) as total from legh_money_receipt,bill_register where bill_register.id=legh_money_receipt.bill_id) " \
                 "from bill_register_line,bill_register where bill_register_line.bill_register_id=bill_register.id and bill_register.state='confirmed' and " \
                 "(bill_register.create_date <= '%s') and (bill_register.create_date >= '%s') " \
                 "group by bill_register_line.name, bill_register_line.department order by bill_register_line.department"

        mri_ct = "select (select examination_entry.name from examination_entry where examination_entry.id=bline.name) as testname,count(bline.price),sum(bline.price) from " \
                 " bill_register as bill,bill_register_line as bline where bill.id=bline.bill_register_id and bline.department in ('MRI','CT Scan') and (bill.create_date <= '%s')" \
                 " and (bill.create_date >= '%s') and " \
                 "bill.state='confirmed' group by testname"

        admission_query = "select sum(legh_admission_line.total_amount) as tm,count(legh_admission_line.total_amount) as tv, " \
                          "(select examination_entry.name from examination_entry where examination_entry.id=legh_admission_line.name) as name,legh_admission_line.department " \
                          "from legh_admission_line,legh_admission where legh_admission_line.legh_admission_id=legh_admission.id " \
                          "and (legh_admission.create_date <='%s') and (legh_admission.create_date >='%s') " \
                          "group by legh_admission_line.name, legh_admission_line.department"

        diagnostic_query="select bl.department,e.name,count(bl.name),bl.price,sum(bl.price) from bill_register as b,bill_register_line as bl,examination_entry as e " \
                         "where bl.bill_register_id=b.id and bl.name=e.id and diagonostic_bill=True and (b.create_date <= '%s') and" \
                         " (b.create_date >= '%s') group by bl.department,e.name,bl.price order by bl.department"

        diagnostic_income="select sum(bill_total_amount) as Total,sum(b.other_discount) as Discount,sum(b.doctors_discounts), sum(lmr.amount) as paid, sum(lmr.due_amount) as due from bill_register as b," \
                          "legh_money_receipt as lmr where b.id=lmr.bill_id and (lmr.create_date <= '%s') and (lmr.create_date >= '%s') and lmr.state!='cancel' " \
                          " and b.diagonostic_bill=True"

        others_investigation="select bl.department,e.name,count(bl.name),bl.price,sum(bl.price) from bill_register as b,bill_register_line as bl,examination_entry as e " \
                             "where bl.bill_register_id=b.id and bl.name=e.id and (diagonostic_bill=FALSE OR diagonostic_bill IS NULL) and (b.create_date <= '%s') and " \
                             "(b.create_date >= '%s') group by bl.department,e.name,bl.price order by bl.department"
        others_income="select sum(bill_total_amount) as Total,sum(b.other_discount) as Discount,sum(b.doctors_discounts), sum(lmr.amount) as paid, sum(lmr.due_amount) as due from bill_register as b," \
                      "legh_money_receipt as lmr where b.id=lmr.bill_id and (lmr.create_date <= '%s') and " \
                      "(lmr.create_date >= '%s') and (b.diagonostic_bill=FALSE or b.diagonostic_bill IS NULL) and lmr.state!='cancel'"

        aadmission_query="select al.department,e.name,count(al.name),al.price,sum(al.price) from legh_admission as a,legh_admission_line as al,examination_entry as e " \
                         "where al.legh_admission_id=a.id and al.name=e.id and (a.create_date <= '%s') and (a.create_date >= '%s') " \
                         "and a.state='activated' group by al.department,e.name,al.price order by al.department"

        admission_income="select sum(lmr.bill_total_amount) as Total,sum(a.other_discount) as Discount,sum(a.doctors_discounts), sum(lmr.amount) as paid, sum(lmr.due_amount) as due from legh_admission as a," \
                         "legh_money_receipt as lmr where a.id=lmr.admission_id and (lmr.create_date <= '%s') and (lmr.create_date >= '%s') and lmr.state!='cancel'"



        #new method of trying details reports






        self.cr.execute(diagnostic_query % (end_date,st_dat))
        result_dict={}
        diagnostic=[]
        for items in self.cr.fetchall():
            diagnostic.append(items)
        result_dict['diagnostic']=diagnostic


        self.cr.execute(diagnostic_income % (end_date,st_dat))
        diag_income = []
        for items in self.cr.fetchall():
            new_list=[]
            for item in items:
                if item==None:
                    item=int(0)
                    new_list.append(item)
                else:
                    item=item
                    new_list.append(item)

            diag_income.append(new_list)


        result_dict['diagnostic_income'] = diag_income

        self.cr.execute(opd_component_q % (end_date,st_dat))
        opd_income = []
        for items in self.cr.fetchall():
            opd_income.append(items)

        result_dict['opd_income'] = opd_income


        self.cr.execute(others_investigation % (end_date,st_dat))
        other_investigations=[]
        for items in self.cr.fetchall():
            other_investigations.append(items)

        result_dict['other_investigations']=other_investigations

        self.cr.execute(others_income % (end_date,st_dat))
        other_incomes=[]
        for items in self.cr.fetchall():
            new_list=[]
            for item in items:
                if item==None:
                    item=int(0)
                    new_list.append(item)
                else:
                    item=item
                    new_list.append(item)
            other_incomes.append(new_list)

        result_dict['other_incomes']=other_incomes

        self.cr.execute(aadmission_query % (end_date,st_dat))
        admission_query=[]
        for items in self.cr.fetchall():
            admission_query.append(items)
        result_dict['admission_query']=admission_query
        # import pdb
        # pdb.set_trace()


        self.cr.execute(admission_income % (end_date,st_dat))
        admission_incomes=[]
        for items in self.cr.fetchall():
            new_list=[]
            for item in items:
                if item==None:
                    item=int(0)
                    new_list.append(item)
                else:
                    item=item
                    new_list.append(item)
            admission_incomes.append(new_list)
        result_dict['admission_incomes']=admission_incomes

        # import pdb
        # pdb.set_trace()

        return result_dict







        # ## It sis For BIll Data Collction
        # self.cr.execute(opd_component_q % (end_date,st_dat))
        # participant_ids = []
        # opd_info = []
        # for items in self.cr.fetchall():
        #     opd_info.append({
        #         'test_name':items[2],
        #         'test_count':items[1],
        #         'test_amnt':items[0],
        #         'test_dept':'OPD',
        #     })
        #
        #
        # ## Bill Collction Ends Here
        #
        # ## It sis For Addmission Data Collction
        #
        # self.cr.execute(bill_q % (end_date, st_dat))
        # for items in self.cr.fetchall():
        #     opd_info.append({
        #         'test_name': items[2],
        #         'test_count': items[1],
        #         'test_amnt': items[0],
        #         'test_dept': items[3],
        #     })
        #
        #     self.cr.execute(mri_ct % (end_date, st_dat))
        #     for items in self.cr.fetchall():
        #         # import pdb
        #         # pdb.set_trace()
        #         opd_info.append({
        #             'test_name': items[0],
        #             'test_count': items[1],
        #             'test_amnt': items[2],
        #             'test_dept': 'MRI_CT',
        #         })
        #
        # ## Addmission Collction Ends Here
        #
        # ## It sis For Addmission Data Collction
        # self.cr.execute(admission_query % (end_date,st_dat))
        #
        # for items in self.cr.fetchall():
        #     opd_info.append({
        #         'test_name': items[2],
        #         'test_count': items[1],
        #         'test_amnt': items[0],
        #         'test_dept': items[3],
        #     })
        # ## Addmission Collction Ends Here
        #
        #
        # return opd_info

    def _get_context_text(self, t_dat=None, end_date=None):
        datestr=str(t_dat)

        datetimeobj=datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
        newtime = datetimeobj + timedelta(hours=6)
        newformate=newtime.strftime("%d-%m-%Y %H:%M:%S")

        datestr=str(end_date)

        datetimeobjs=datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
        newtimes = datetimeobjs + timedelta(hours=6)
        newformates=newtimes.strftime("%d-%m-%Y %H:%M:%S")


        # import pdb
        # pdb.set_trace()
        txt = "Start Date " + newformate  + " End Date " + newformates
        return txt

    def __init__(self, cr, uid, name, context):



        super(detail_collcetion_details, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_user_names': self._get_user_names,
            'get_user_context': self._get_context_text,
        })


class report_detail_component(osv.AbstractModel):
    _name = 'report.legh.report_detail_component'
    _inherit = 'report.abstract_report'
    _template = 'legh.report_detail_component'
    _wrapped_report_class = detail_collcetion_details
