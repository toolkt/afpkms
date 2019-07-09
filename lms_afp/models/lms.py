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





class LMSPartner(models.Model):
    _name = "lms.partner"
    _description = 'LMS Partner'
    
    @api.model
    def _default_image(self):
        image_path = get_module_resource('lms', 'static/src/img', 'default_avatar_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        course = super(LMSCourse, self).create(vals)
        return course

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(LMSCourse, self).write(vals)
        return res

    name = fields.Char('Name')

    first_name = fields.Char('First Name')
    middle_name = fields.Char('Middle Name')
    last_name = fields.Char('Last Name')
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
        tools.image_resize_images(vals)
        course = super(LMSCourse, self).create(vals)
        return course

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
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



    @api.one
    @api.depends('line_ids.state')
    def _compute_count(self):
        self.progress = 10



class LMSCourseLine(models.Model):
    _name = "lms.course.line"
    _description = 'Course Outline'
    _order = 'sequence'
    
    name = fields.Char('Section Name')
    sequence = fields.Integer(default=10, help="Gives the sequence of this line when displaying the course outline.")
    description = fields.Char('Description')
    info = fields.Html('Information')
    date_from = fields.Date("Date from")
    date_to = fields.Date("Date to")
    course_id = fields.Many2one('lms.course','Course')
    state = fields.Selection([('pending','Pending'),('start','Started'),('completed','Completed')],default='pending',string="State")





