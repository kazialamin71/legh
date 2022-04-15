from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time, datetime
from openerp import api


class opd_ticket(osv.osv):
    _name = "opd.ticket"
    _order = 'id desc'




    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("opd.ticket").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.opd_ticket_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum=item+sum


                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum
                    # import pdb
                    # pdb.set_trace()
        return Percentance_calculation


    _columns = {

        # 'patient_id': fields.char("Patient ID"),
        'name':fields.char("Name"),
        'mobile': fields.char(string="Mobile",store=False),
        'patient_id': fields.char(related='patient_name.patient_id',string="Patient Id",readonly=True),
        'patient_name': fields.many2one('patient.info', "Patient Name"),
        'address': fields.char("Address",store=False),
        'age': fields.char("Age",store=False),
        'sex':fields.char("Sex",store=False),
        'already_collected':fields.boolean("Money Collected",default=False),
        # 'date':fields.datetime("Date", readonly=True,default=lambda self: fields.datetime.now()),
        'date':fields.date("Date", readonly=True,default=lambda self: fields.datetime.now()),
        'ref_doctors': fields.many2one('doctors.profile','Reffered by'),
        'opd_ticket_line_id': fields.one2many('opd.ticket.line', 'opd_ticket_id', 'Investigations',required=True),
        'user_id': fields.many2one('res.users', 'Assigned to', select=True, track_visibility='onchange'),
        'state': fields.selection(
            [('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'Status', default='confirmed', readonly=True),
        'total': fields.float(string="Total")
    }
    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        # 'opd_ticket_line_id':[[0, False, {'department': 'Medicine', 'price': 100, 'name': 1, 'total_amount': 100}]],
    }

    def opd_cancel(self, cr, uid, ids, context=None):
        cr.execute("select id as jounral_id from account_move where ref = (select name from opd_ticket where id=%s limit 1)",(ids))
        joural_ids = cr.fetchall()
        context = context

        itm = [itm[0] for itm in joural_ids]
        if len(itm) > 0:
            uid = 1
            moves = self.pool.get('account.move').browse(cr, uid, itm, context=context)
            moves.button_cancel()  ## Cancelling
            moves.unlink()  ### Deleting Journal

        #### Ends Here

        ## Bill Status Will Change

        cr.execute("update opd_ticket set state='cancelled' where id=%s", (ids))
        cr.commit()
        return "C"


    def onchange_total(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('legh.tests').browse(cr, uid, name, context=None)
        abc = {'total': dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_patient(self,cr,uid,ids,name,context=None):
        tests={}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc={'mobile':dep_object.mobile,'address':dep_object.address,'age':dep_object.age,'sex':dep_object.sex}
        tests['value']=abc
        return tests





    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(opd_ticket, self).create(cr, uid, vals, context) # return ID int object

        if stored is not None:

            name_text = 'OPD-0' + str(stored)
            cr.execute('update opd_ticket set name=%s where id=%s', (name_text, stored))
            cr.commit()
            stored_obj = self.browse(cr, uid,stored, context=context)

            ###OPD JOurnal Start Here
            if stored_obj:

                line_ids = []

                if context is None: context = {}
                if context.get('period_id', False):
                    return context.get('period_id')
                periods = self.pool.get('account.period').find(cr, uid, context=context)
                period_id = periods and periods[0] or False
                has_been_paid = stored_obj.total

                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': 6,  ### Cash ID
                    'debit': has_been_paid,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

                for cc_obj in stored_obj.opd_ticket_line_id:
                    # import pdb
                    # pdb.set_trace()
                    total = 0

                    if cc_obj.name.name:
                        # ledger_id = 611
                        # try:
                        #     ledger_id = cc_obj.name.accounts_id.id
                        # except:
                        #     ledger_id = 611  ## Diagnostic Income Head , If we don't assign any Ledger

                        if context is None:
                            context = {}

                        line_ids.append((0, 0, {
                            'analytic_account_id': False,
                            'tax_code_id': False,
                            'tax_amount': 0,
                            'name': cc_obj.name.name,
                            'currency_id': False,
                            'account_id': cc_obj.name.accounts_id.id,
                            'credit': cc_obj.total_amount,
                            'date_maturity': False,
                            'debit': 0,
                            'amount_currency': 0,
                            'partner_id': False,
                        }))
                    # import pdb
                    # pdb.set_trace()

                jv_entry = self.pool.get('account.move')

                j_vals = {'name': '/',
                          'journal_id': 2,  ## Sales Journal
                          'date': stored_obj.date,
                          'period_id': period_id,
                          'ref': stored_obj.name,
                          'line_id': line_ids

                          }

                # import pdb
                # pdb.set_trace()

                saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                if saved_jv_id > 0:
                    journal_id = saved_jv_id
                    try:

                        jv_entry.button_validate(cr, uid, [saved_jv_id], context)
                    except:
                        import pdb
                        pdb.set_trace()

               ###ENd of Journal
            return stored




    @api.onchange('opd_ticket_line_id')
    def onchange_total(self):
        total=0
        for item in self.opd_ticket_line_id:
            total=total+item.total_amount
        self.total=total
        return 'O'



    def write(self, cr, uid, ids,vals,context=None):
        if vals.get('opd_ticket_line_id') or uid == 1:
            cr.execute("select id as journal_ids from account_move where ref = (select name from opd_ticket where id=%s limit 1)",(ids))
            journal_ids = cr.fetchall()
            context=context
            updated = super(opd_ticket, self).write(cr, uid, ids, vals, context=context)
            itm = [itm[0] for itm in journal_ids]
            if len(itm)>0:
                uid=1
                moves =self.pool.get('account.move').browse(cr, uid, itm, context=context)
                xx=moves.button_cancel() ## Cancelling
                moves.unlink()

                stored_obj = self.browse(cr, uid, [ids[0]], context=context)
                if stored_obj:

                    line_ids = []

                    if context is None: context = {}
                    if context.get('period_id', False):
                        return context.get('period_id')
                    periods = self.pool.get('account.period').find(cr, uid, context=context)
                    period_id = periods and periods[0] or False
                    has_been_paid = stored_obj.total

                    line_ids.append((0, 0, {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'tax_amount': 0,
                        'name': stored_obj.name,
                        'currency_id': False,
                        'credit': 0,
                        'date_maturity': False,
                        'account_id': 6,  ### Cash ID
                        'debit': has_been_paid,
                        'amount_currency': 0,
                        'partner_id': False,
                    }))

                    for cc_obj in stored_obj.opd_ticket_line_id:
                        # import pdb
                        # pdb.set_trace()
                        total = 0

                        if cc_obj.name.name:
                            # ledger_id = 611
                            # try:
                            #     ledger_id = cc_obj.name.accounts_id.id
                            # except:
                            #     ledger_id = 611  ## Diagnostic Income Head , If we don't assign any Ledger

                            if context is None:
                                context = {}

                            line_ids.append((0, 0, {
                                'analytic_account_id': False,
                                'tax_code_id': False,
                                'tax_amount': 0,
                                'name': cc_obj.name.name,
                                'currency_id': False,
                                'account_id': cc_obj.name.accounts_id.id,
                                'credit': cc_obj.total_amount,
                                'date_maturity': False,
                                'debit': 0,
                                'amount_currency': 0,
                                'partner_id': False,
                            }))
                        # import pdb
                        # pdb.set_trace()

                    jv_entry = self.pool.get('account.move')

                    j_vals = {'name': '/',
                              'journal_id': 2,  ## Sales Journal
                              'date': stored_obj.date,
                              'period_id': period_id,
                              'ref': stored_obj.name,
                              'line_id': line_ids

                              }

                    # import pdb
                    # pdb.set_trace()

                    saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                    if saved_jv_id > 0:
                        journal_id = saved_jv_id
                        try:

                            jv_entry.button_validate(cr, uid, [saved_jv_id], context)
                        except:
                            import pdb
                            pdb.set_trace()
                    return updated
                    ### Ends the journal Entry Here
            else:
                updated = super(opd_ticket, self).write(cr, uid, ids, vals, context=context)
                # raise osv.except_osv(_('Warning!'),
                #                      _("You cannot Edit the bill"))
                return updated







class test_information(osv.osv):
    _name = 'opd.ticket.line'

    _columns = {

        'name': fields.many2one("opd.ticket.entry","Item Name",ondelete='cascade'),
        'opd_ticket_id': fields.many2one('opd.ticket', "Information"),
        'price': fields.integer("Price"),
        'department':fields.char('Department'),
        'total_amount': fields.integer("Total Amount")

    }



    # @api.onchange('total_amount')
    # def change_item_price(self):
    #     opd_ticket_line_id=list()
    #     opd_ticket_line_id.append({
    #         'total':500
    #     })
    #
    #     ticket_id=self.opd_ticket_id
    #     return "Nothing"


    def onchange_item(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('opd.ticket.entry').browse(cr, uid, name, context=None)
        abc = {'price': dep_object.fee,'department':dep_object.department.name,'total_amount':dep_object.fee}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests



