from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat

from odoo.addons.formio.utils import get_field_selection_label


class LMSCourse(models.Model):
    _inherit = "lms.course"

    form_ids = fields.Many2many('formio.builder','lms_course_builder_ids','course_id','builder_id','Available Forms')
    # submitted_form_ids = fields.One2many(comodel_name='formio.form', compute='_compute_my_form_ids')
    # available_payment_method_ids = fields.One2many(comodel_name='account.payment', compute='_compute_available_payment_method_ids')


    def _compute_my_form_ids(self):
        for rec in self:
            rec.submitted_form_ids = []
    # @api.depends('journal_id', 'batch_type')
    # def _compute_available_payment_method_ids(self):
    #     for record in self:
    #         record.available_payment_method_ids = record.batch_type == 'inbound' and record.journal_id.inbound_payment_method_ids.ids or record.journal_id.outbound_payment_method_ids.ids


class Builder(models.Model):
    _inherit = 'formio.builder'

    course_id = fields.Many2one('lms.course', "Course ID")

    @api.multi
    def action_open_my_form(self):
        for rec in self:
            # ctx = self.parent_id
            # print (ctx)
            my_form = self.env['formio.form'].search([('user_id','=',self.env.uid),('builder_id','=',rec.id)], limit=1)
            if not my_form:
                my_form = self.env['formio.form'].create({'builder_id':rec.id, 'user_id':self.env.uid})

            form = my_form.action_formio()
            # form['url'] = '%s%s' % (form['url'],"?test")
            # print(form)
            return form


class Form(models.Model):
    _inherit = 'formio.form'

    course_id = fields.Many2one('lms.course',"Course")

    def _compute_res_fields(self):
        for rec in self:
            #Edit this
            course = self.env['lms.course'].search([],limit=1)
            action = self.env.ref('lms.lms_course_action_form')
            url = '/web?#id={id}&view_type=form&model={model}&action={action}'.format(
                id=course.id,
                model='lms.course',
                action=action.id)
            rec.res_act_window_url = url
            print (url)
            rec.res_name = course.name
            rec.res_info = course.name
             
