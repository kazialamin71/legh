from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class hospital_dashboard(osv.osv):
    _name = "hospital.dashboard"

    def dashboard_data(self, cr, uid, start_date=None, end_date=None, context=None):

        v1 = v2 = v3 = v4 = v5 = v6 = v7 = v8 = 0


        cr.execute("select sum(total) as total from bill_register")
        all_data = cr.fetchall()
        if len(all_data) >0:
            v1=all_data[0][0]

        ## Cash Collection Query
        cr.execute("select sum(total) as total from cash_collection")
        all_data = cr.fetchall()
        if len(all_data) >0:
            v2=all_data[0][0]





        cr.execute("select sum(total) as total, ref_doctors, (select name from doctors_profile where doctors_profile.id=ref_doctors) as dr_name from bill_register group by ref_doctors limit 10")
        doctor_data = cr.fetchall()
        collection_overview_data = []

        collection_overview_data_lebel =[]

        for items in doctor_data:
            if items[1] >0:
                collection_overview_data_lebel.append(items[2])
                collection_overview_data.append(items[0])
            else:
                collection_overview_data_lebel.append('Others')
                collection_overview_data.append(items[0])

        cr.execute(
            "select count(id) from patient_info")
        patient_data = cr.fetchall()
        if len(patient_data) >0:
            v3=v4 = patient_data[0][0]

        cr.execute(
            "select count(id) from diagnosis_sticker")
        test_data = cr.fetchall()
        if len(test_data) > 0:
            v5 = v6 = test_data[0][0]

        cr.execute(
            "select sum(amount) from legh_expense")
        expense_data = cr.fetchall()
        if len(expense_data) > 0:
            v7 = expense_data[0][0]
            v8=4


        pending_for_assignment = "Income Summary : " +str(v1)
        assigned = "Total Cash Collected : "+str(v2)
        pending_submit = "Total Patients : " +str(v3)
        overdue_submit = "New Patients : " +str(v4)
        pending_payment = "Total Tests : " +str(v5)
        overdue_payment = "Only Pathology : " +str(v6)
        pending_collection = "Total Expense : " +str(v7)
        total_collected = "Total Expense Head Count : " +str(v8)


        cr.execute("select sum(amount), expense_type from legh_expense group by expense_type")
        expense_data_type_wise=cr.fetchall()
        all_user_list=[]
        all_user_value_list=[]


        for item in expense_data_type_wise:
            all_user_list.append(item[0])
            all_user_value_list.append(item[0])









        result_list =[pending_for_assignment,assigned,pending_submit,overdue_submit,pending_payment,overdue_payment,pending_collection,total_collected,collection_overview_data_lebel,collection_overview_data,all_user_list,all_user_value_list]
        return result_list









    _columns = {
        'name':fields.char('Name')

    }


