
from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time, timedelta, datetime

class cash_collection(osv.osv):
    _name = "cash.collection"



    @api.onchange('type')
    def _onchange_tpe(self):
        child_list=[]
        total=0

        # mr_obj = self.pool.get("leih.money.receipt").search(self.cr, self.uid, [('date','>=',self.date)])
        if self.type=='bill':
            vals_parameter = [('bill_id', '!=', False),('diagonostic_bill', '=', True),('already_collected','!=',True),('state','!=','cancel')]
            if self.date:
                vals_parameter.append(('date','=',self.date))
            mr_obj=self.env['leih.money.receipt'].search(vals_parameter)

            for record in mr_obj:
                abc = {}
                abc['bill_admission_opd_id']=record.bill_id.name
                abc['mr_no']=record.id
                abc['amount']=record.amount
                total = total +record.amount
                child_list.append([0, False, abc])

        if self.type=='bill_others':
            vals_parameter = [('bill_id', '!=', False),('diagonostic_bill', '!=', True),('already_collected','!=',True),('state','!=','cancel')]
            if self.date:
                vals_parameter.append(('date','=',self.date))
            mr_obj=self.env['leih.money.receipt'].search(vals_parameter)

            for record in mr_obj:
                abc = {}
                abc['bill_admission_opd_id']=record.bill_id.name
                abc['mr_no']=record.id
                abc['amount']=record.amount
                total = total +record.amount
                child_list.append([0, False, abc])


        if self.type=='admission':
            vals_parameter = [('admission_id', '!=', False), ('already_collected', '!=', True),('state','!=','cancel')]
            if self.date:
                vals_parameter.append(('date', '=', self.date))
            mr_obj=self.env['leih.money.receipt'].search(vals_parameter)

            for record in mr_obj:
                abc = {}
                abc['bill_admission_opd_id']=record.admission_id.name
                abc['mr_no']=record.id
                abc['amount']=record.amount
                total = total + record.amount
                child_list.append([0, False, abc])

        if self.type=='optics':
            vals_parameter = [('optics_sale_id', '!=', False),('already_collected','!=',True),('state','!=','cancel')]
            if self.date:
                vals_parameter.append(('date','=',self.date))
            mr_obj=self.env['leih.money.receipt'].search(vals_parameter)

            for record in mr_obj:
                abc = {}
                abc['bill_admission_opd_id']=record.optics_sale_id.name
                abc['mr_no']=record.id
                abc['amount']=record.amount
                total = total +record.amount
                child_list.append([0, False, abc])

        if self.type=='opd':
            vals_parameter = [('already_collected', '!=', True)]
            if self.date:
                vals_parameter.append(('date', '=', self.date))
            mr_obj=self.env['opd.ticket'].search(vals_parameter)
            # import pdb
            # pdb.set_trace()

            for record in mr_obj:
                abc = {}
                abc['bill_admission_opd_id']=record.name
                abc['opd_id']=record.id
                abc['amount']=record.total
                total = total + record.total
                child_list.append([0, False, abc])


        self.total=total

        self.cash_collection_lines = child_list

    def action_button_confirm(self, cr, uid, ids, context=None):
        contex = context
        cc_ids=ids
        for id in cc_ids:
            ids =[id]
            cc_obj = self.browse(cr, uid,ids , context=context)
            if cc_obj.state == 'approve':
                raise osv.except_osv(_('Already Confirmed'), _('Sorry, it is already confirmed'))
            else:
                ## start create journal from here

                if context is None: context = {}
                if context.get('period_id', False):
                    return context.get('period_id')
                periods = self.pool.get('account.period').find(cr, uid, context=context)
                period_id= periods and periods[0] or False

                if context is None:
                    context = {}

                line_ids = []

                line_ids.append((0, 0, {
                    'name':  cc_obj.name,
                    'account_id': cc_obj.debit_act_id.id,
                    'debit': cc_obj.total,
                }))

                line_ids.append((0, 0, {
                    'name':cc_obj.name,
                    'account_id': cc_obj.credit_act_id.id,
                    'credit': cc_obj.total,
                }))

                j_vals = {'name': '/',
                          'journal_id': 2,  ## Sales Journal
                          'date': fields.date.today(),
                          'period_id': period_id,
                          'ref': cc_obj.name,
                          'line_id': line_ids

                          }

                jv_entry = self.pool.get('account.move')

                saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                if saved_jv_id > 0:
                    journal_id = saved_jv_id
                jv_entry.button_validate(cr, uid, [saved_jv_id], context)

                ## Ends here


                ## Confirm the Cash Colletion And flaggin the MR's

                confirm_cash_collection_query = "UPDATE cash_collection SET state='approve',journal_id={0} WHERE id={1}".format(saved_jv_id, id)
                cr.execute(confirm_cash_collection_query)
                cr.commit()


                ## Flagging


                try:
                    for line_items in cc_obj.cash_collection_lines:
                        if line_items.mr_no.id != False:
                            mr_id = line_items.mr_no.id
                            cr.execute( "UPDATE leih_money_receipt SET already_collected=True WHERE id={0}".format(mr_id))
                            cr.commit()
                        else:
                            mr_id = line_items.opd_id.id
                            cr.execute("UPDATE opd_ticket SET already_collected=True WHERE id={0}".format(mr_id))
                            cr.commit()




                except:
                    pass


                ## Ends here Cash collection and Flagging




        return True



    def action_button_cancel(self, cr, uid, ids, context=None):
        return True





    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}

        stored = super(cash_collection, self).create(cr, uid, vals, context) # return ID int object


        if stored is not None:
            name_text = 'Cash-0' + str(stored)
            cr.execute('update cash_collection set name=%s where id=%s', (name_text, stored))
            cr.commit()



        return stored


    _columns = {

        'name': fields.char("Cash Collection No"),
        # 'date': fields.date("Date"),
        'date': fields.datetime("Date", default=lambda self: fields.datetime.now()),
        'type': fields.selection([('bill','Bill [Diagnosis]'),('bill_others','Bill [others]'),('opd','OPD'),('admission','Admission'),('optics','Optics')], 'Type'),
        'total': fields.float("Total"),
        'journal_id':fields.many2one('account.move', 'Journal '),
        'debit_act_id':fields.many2one('account.account', 'Debit Account ', required=True),
        'credit_act_id':fields.many2one('account.account', 'Credit Account ', required=True),
        'cash_collection_lines': fields.one2many("cash.collection.line","cash_collection_line_id",'cash collection', required=True),
         'state': fields.selection([
           ('pending', 'Pending'),
           ('approve', 'Confirmed'),
            ('cancel', 'Cancelled')], 'State', default = 'pending', readonly = True),

    }

    _defaults = {
        'state': 'pending',

    }

    _order = 'id desc'



class cash_collection_line(osv.osv):
    _name="cash.collection.line"

    _columns = {
        'cash_collection_line_id':fields.many2one("cash.collection","Cash Collection"),
        'mr_no':fields.many2one('leih.money.receipt', 'MR No. '),
        'opd_id':fields.many2one('opd.ticket', 'OPD No. '),
        'bill_admission_opd_id':fields.char("Bill/Admission/OPD Number"),
        'amount':fields.float("Amount")
    }