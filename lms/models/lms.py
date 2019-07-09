# -*- coding: utf-8 -*-
import base64
import datetime
import hashlib
import pytz
import threading
import re

from email.utils import formataddr
from dateutil.relativedelta import relativedelta

import requests
from lxml import etree
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat



def get_years():
    year_list = []
    for i in range(2016, 2036):
        year_list.append((i, str(i)))
    return year_list

def get_months():
    return [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                              (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
                              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]



class LMSCourseCategory(models.Model):
    _name = "lms.course.category"
    _description = 'Course Category'
    _order = 'sequence'
    
    name = fields.Char('Category Name')
    sequence = fields.Integer(default=10, help="Gives the sequence of this line when displaying the category.")
    color = fields.Integer(string='Color Index')





class LMSPartner(models.Model):
    _name = "lms.partner"
    _description = 'LMS Partner'
    
    @api.model
    def _default_image(self):
        image_path = get_module_resource('lms', 'static/src/img', 'default_avatar_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals, sizes={'image': (1024, None)})
        course = super(LMSPartner, self).create(vals)
        return course

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals, sizes={'image': (1024, None)})
        res = super(LMSPartner, self).write(vals)
        return res

    @api.one
    @api.depends('first_name','middle_name','last_name')
    def _get_full_name(self):
        first_name, middle_name, last_name = "","",""

        if self.first_name:
            first_name = self.first_name
        if self.middle_name:
            middle_name = self.middle_name
        if self.last_name:
            last_name = self.last_name

        self.name = "%s, %s %s" % (last_name,first_name,middle_name)


    name = fields.Char('Name', compute="_get_full_name", store=True)
    user_id = fields.Many2one('res.users', string='Student')

    first_name = fields.Char('First Name')
    middle_name = fields.Char('Middle Name')
    last_name = fields.Char('Last Name')
    email = fields.Char('Email')
    gender = fields.Selection([('M','Male'),('F','Female')], "Gender")

    description = fields.Char('Description')
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Photo", default=_default_image, attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")


    partner_image = fields.Binary(string='Photo', related='user_id.partner_id.image', readonly=False)
    partner_image_medium = fields.Binary(
        "Medium-sized photo", related='user_id.partner_id.image_medium')
    partner_image_small = fields.Binary(
        "Small-sized photo", related='user_id.partner_id.image_small')


    student = fields.Boolean('Is a Student')
    faculty = fields.Boolean('Is a Faculty')



    #For AFP
    info_afpsn = fields.Char("AFP SN")
    info_blood_type = fields.Char("Blood Type")
    info_bos = fields.Selection([('ARMY','ARMY'),('AIRFORCE','AIRFORCE'),('NAVY','NAVY')],"Branch of Service")


class LMSCourse(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']	
    _name = "lms.course"
    _description = 'Courses'
    _order = 'sequence'
    

    @api.model
    def _default_image(self):
        image_path = get_module_resource('lms', 'static/src/img', 'default_course_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals, sizes={'image': (1024, None)})
        course = super(LMSCourse, self).create(vals)
        return course

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals, sizes={'image': (1024, None)})
        res = super(LMSCourse, self).write(vals)
        return res

    name = fields.Char('Course Name')
    active = fields.Boolean(default=True, help="If the active field is set to False, it will allow you to hide the course without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence of this line when displaying the csourses.")
    description = fields.Char('Description')
    info = fields.Text('Information')
    image = fields.Binary('Image', attachment=True)
    line_ids = fields.One2many('lms.course.line','course_id','Outline')
    category_ids = fields.Many2many('lms.course.category',string='Category')
    progress = fields.Integer(string="Progress", compute="_compute_count")
    activity_count = fields.Integer(string="Activities", compute="_compute_count")

    color = fields.Integer(string='Color Index')
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Photo", default=_default_image, attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")


    student_ids = fields.Many2many('lms.partner','course_partner_student_rel','course_id','partner_id','Students', 
        domain=[('student','=',True)])

    faculty_ids = fields.Many2many('lms.partner','course_partner_faculty_rel','course_id','partner_id','Faculty', 
        domain=[('faculty','=',True)])

    group_ids = fields.One2many('lms.course.group','course_id','Groups')

    user_ids = fields.Many2many('res.users', compute='_get_users', store=True)

    submission_ids = fields.One2many(comodel_name='lms.course.line.submission', compute='_compute_lms_course_line_submission')
    all_submission_ids = fields.One2many(comodel_name='lms.course.line.submission', compute='_compute_lms_course_line_submission')



    def _compute_lms_course_line_submission(self):
        for rec in self:
            rec.submission_ids = self.env['lms.course.line.submission'].search([('user_id','=',self.env.user.id),('course_line_id','!=',False)])

            query = """
                SELECT ls.id from lms_course_line_submission ls
                left join lms_course_line l on l.id = ls.course_line_id
                left join lms_course c on c.id = l.course_id
                where c.id = %s
            """ % rec.id

            self.env.cr.execute(query)
            rec.all_submission_ids = [r[0] for r in self.env.cr.fetchall()]


    @api.multi
    def action_calendar_activity(self):
        self.ensure_one()
        return {
            'name': 'Activities',
            'domain': [('course_id', '=', self.id)],
            'view_type': 'calendar',
            'view_mode': 'calendar',
            'res_model': 'lms.course.line',
            'view_id': self.env.ref('lms.lms_course_line_student_calendar').id,
            'type': 'ir.actions.act_window',
            'res_id': False,
        }



    @api.depends('line_ids')
    def _compute_count(self):

        for rec in self:
            rec.progress = 0
            counter = 0
            completed = 0

            for a in rec.line_ids:
                if a.activity == True:
                    counter += 1
                if a.state == 'completed':
                    completed += 1

            if counter > 0:
                rec.progress = round((completed/counter)*100)

            rec.activity_count = counter
        

    @api.depends('student_ids','faculty_ids')
    def _get_users(self):
        for rec in self:
            users = []
            for s in rec.student_ids:
                uid = s.user_id.id
                if uid not in users:
                    users.append(uid)
 
            for f in rec.faculty_ids:
                uid = f.user_id.id
                if uid not in users:
                    users.append(uid) 

            for a in self.env.ref('lms.group_lms_admin').users:
                uid = a.id
                if uid not in users:
                    users.append(uid) 

            rec.user_ids = users

class LMSCourseLine(models.Model):
    _name = "lms.course.line"
    _inherit = ['mail.thread']
    _description = 'Course Outline'
    _order = 'sequence'
    
    name = fields.Char('Section Name')
    sequence = fields.Integer(default=10, help="Gives the sequence of this line when displaying the course outline.")
    description = fields.Char('Description')
    info = fields.Text('Information')
    date_from = fields.Datetime("Date from")
    date_to = fields.Datetime("Date to")
    course_id = fields.Many2one('lms.course','Course')
    activity = fields.Boolean('Is an Activity', default=True, help="If checked it will be computed as part of the course progress bar")
    turnin = fields.Boolean('With Turn-in', default=False, help="If checked it show the turnin button")
    state = fields.Selection([('pending','Pending'),('start','Started'),('completed','Completed')],default='pending',string="State")
    group_id = fields.Many2one('lms.course.group','Groups')
    attachment_ids = fields.Many2many('ir.attachment', 'lms_course_line_attachment_rel', 'lms_course_line_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this template, to be added to all "
                                           "emails created from this template")

    faculty_ids = fields.Many2many('lms.partner','course_line_faculty_rel','course_line_id','partner_id','Instructor', 
        domain=[('faculty','=',True)])
    record_id = fields.Many2one('lms.course.line', "Name", compute='_get_current_record')


    @api.multi
    def _get_current_record(self):
        for rec in self:
           rec.record_id = rec.id


    @api.multi
    def action_go_to_activity(self):
        for rec in self:
            return {
                'name': 'Activity',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'lms.course.line',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': rec.id,
            }


    @api.multi
    def action_submission_wizard(self):
        for rec in self:
            submissions = self.env['lms.course.line.submission'].search([('user_id','=',self.env.uid),('course_line_id','=',rec.id)], limit=1)
            
            if not submissions: 
                submissions = self.env['lms.course.line.submission'].create({'user_id': self.env.uid, 'course_line_id' : rec.id})

            return {
                'name': 'Submission',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'lms.course.line.submission',
                'type': 'ir.actions.act_window',
                'res_id': submissions.id,
                'target': 'inline',
            }
             


    @api.multi
    def action_close(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class LMSCourseGroup(models.Model):
    _name = "lms.course.group"

    name = fields.Char('Group Name')
    course_id = fields.Many2one('lms.course', "Course")
    group_type = fields.Selection([('include','Include'),('except','Except')],"Group Type", default='include')
    student_ids = fields.Many2many('lms.partner','course_group_partner_student_rel','course_group_id','partner_id','Students', 
        domain=[('student','=',True)])



class LMSCourseLineSubmission(models.Model):
    _name = "lms.course.line.submission"
    _inherit = ['mail.thread']
    _description = 'Course Line Submissions'


    user_id = fields.Many2one('res.users', string='Student')
    course_line_id = fields.Many2one('lms.course.line',"Activity")
    state = fields.Selection([('draft','Draft'),('submitted','Submitted')],"State", default='draft')
    attachment_ids = fields.Many2many('ir.attachment', 'lms_course_line_submission_attachment_rel', 'lms_course_line_submission_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this template, to be added to all "
                                           "emails created from this template")

    attachment2_ids = fields.Many2many('ir.attachment', 'lms_course_line_submission_attachment_rel', 'lms_course_line_submission_id',
                                      'attachment_id', 'Attachments2',
                                      help="You may attach files to this template, to be added to all "
                                           "emails created from this template")


    @api.multi
    def action_submit(self):
        for rec in self:
            rec.write({'state':'submitted'})
            return {
                'name': 'Activity',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'lms.course.line',
                'type': 'ir.actions.act_window',
                'res_id': rec.course_line_id.id,
                'tag': 'history_back',
            }


