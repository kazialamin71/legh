# Author Mufti Muntasir Ahmed 23/3/19

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time


class test(osv.osv):
    _name = 'diagonosis'

    def action_blf(self, cr, uid, ids, context=None):
        abc = '90000000'

        for id in ids:

            cr.execute("update diagonosis set age=%s where id=%s", ([abc,id]))
        return 0


    def action_quotation_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'sale.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    # def force_quotation_send(self, cr, uid, ids, context=None):
    #     for order_id in ids:
    #         email = self.action_quotation_send(cr, uid, [order_id], context=context)
    #         if email and email.get('context'):
    #             composer_obj = self.pool['mail.compose.message']
    #             composer_values = {}
    #             email_ctx = email['context']
    #             template_values = [
    #                 email_ctx.get('default_template_id'),
    #                 email_ctx.get('default_composition_mode'),
    #                 email_ctx.get('default_model'),
    #                 email_ctx.get('default_res_id'),
    #             ]
    #             composer_values.update(composer_obj.onchange_template_id(cr, uid, None, *template_values, context=context).get('value', {}))
    #             if not composer_values.get('email_from'):
    #                 composer_values['email_from'] = self.browse(cr, uid, order_id, context=context).company_id.email
    #             for key in ['attachment_ids', 'partner_ids']:
    #                 if composer_values.get(key):
    #                     composer_values[key] = [(6, 0, composer_values[key])]
    #             composer_id = composer_obj.create(cr, uid, composer_values, context=email_ctx)
    #             composer_obj.send_mail(cr, uid, [composer_id], context=email_ctx)
    #     return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'diagonosis_except'}, context=context)
        return True



    _columns = {

        'name': fields.char('Name'),
        'patient_id': fields.char('Transaction ID', required=True),
        'present_date': fields.datetime("Test date", required=True),
        'payment': fields.selection([('zero', '00.0'), ('normal', '100'), ('ent', '200'), ('specialist', '300')],
                                    'Amount'),


        'first_name': fields.char('First Name', required=True),
        'last_name': fields.char('Last Name', required=True),

        'father__name': fields.char('Fathers Name'),
        'mother_name': fields.char('Mothers Name'),
        'age': fields.char('Age'),

        'phone': fields.char('Phone No', required=True),
        'email': fields.char('Email'),
        'nid': fields.char('NID'),

        'p_address': fields.text('Peasant Address'),
        'per_address': fields.text('Permanents Address'),

        'gender': fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender'),


    }



        # Create is only for database insert
    # def create(self, cr, uid, vals, context=None):
    #
    #     full_name=None
    #     firstname=None
    #     lastname=None
    #
    #     firstname=vals.get('first_name')
    #     lastname=vals.get('last_name')
    #
    #
    #     full_name = firstname+ ' ' + lastname
    #
    #     vals['name'] = full_name
    #
    #
    #
    #     return super(test, self).create(cr, uid, vals, context=context)
    #
    #
    #     # Write is only for database update
    # def write(self, cr, uid, ids, values, context=None):
    #
    #
    #
    #     return super(test, self).write(cr, uid, ids, values, context=context)


    # def create(self, cr, uid, vals, context=None):


        # ****Debuging Tools****
        # import pdb
        # pdb.set_trace()



    # def create(self, cr, uid, vals, context=None):
    #
    #
    #     y = None
    #     if int(len('phone')) == 11:
    #         y = super(test, self).create(cr, uid, vals, context=context)
    #
    #     elif int(len('phone')) == 13:
    #         y = super(test, self).create(cr, uid, vals, context=context)
    #
    #     elif int(len('phone')) == 14:
    #         y = super(test, self).create(cr, uid, vals, context=context)
    #
    #     else:
    #         raise osv.expect_osv(_('invalid phone number'))
    #
    #     return y
    #




#
# class usercheck(osv.osv):
#     _name = 'user.check'
#
#
#     def _test(self, cr, uid, ids, field_name, arg, context=None):
#
#         res = {}
#         for record in self.browse(cr, uid, ids, context=context):
#             user_age = record.test_user_id.age
#             if user_age > 21:
#                 message = 'His/her age is ' + str(user_age) + ' ans allowed to create ana account'
#             else:
#                 message = 'His/her age is ' + str(user_age) + ' ans not allowed to create ana account'
#
#             res[record.id] =message
#
#         return res
#
#     def _pers(self, cr, uid, ids, field_name, arg, context=None):
#         res = {}
#         for record in self.browse(cr, uid, ids, context=context):
#             blance =1
#             if record.test_user_id.blance > 0:
#                 blance= record.test_user_id.blance
#             withdrews = record.test_user_id.withdrew
#             if withdrews<= blance:
#
#                 percent = (withdrews*100)/blance
#
#                 message = 'His/her withdrew blance is ' + str(percent) + '% of his/her total blance'
#             else:
#                 massage = 'Insufficiant Amount'
#
#
#             res[record.id] = message
#
#         return res
#
#
#
#
#     _columns = {
#
#         'accptance_rate': fields.integer('Acceptance Rate(%)'),
#         'rejected_rate': fields.integer('Rejected Rate(%)'),
#         'test_user_id': fields.many2one('alu','Emplyee Name',required=True),
#
#
#
#         'alu_age': fields.function(_test, type='char', string='Mufti'),
#         'percent':fields.function(_pers,type='char',string='Percentence')
#
#     }
#
#     def  default_test_user_id(self):
#         return {'age':20}#         return {'age':20}