# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

class CMSDepartment(models.Model):

    _name = 'cms.department'
    _description = 'Department Information'

    name = fields.Char('Name', required=True)
    parent_id = fields.Many2one(
        'cms.department', string='Department', ondelete='restrict', index=True)


class CMSCourse(models.Model):

    _name = 'cms.course'
    _description = 'Course Information'

    name = fields.Char('Name', required=True)
    course_id = fields.Many2one(
        'cms.course', string='Course', ondelete='restrict', index=True)

class CMSAssignment(models.Model):
    _name = 'cms.assignment'
    _description = 'Assignment Information'

    assignment_id = fields.Char("Assignment ID", required=True)
    description = fields.Char("Description", required=True)
    course_ids = fields.Many2one('cms.course', string='Courses')
    date = fields.Date("Date")
    remark = fields.Text('Remark')
    attachment_ids = fields.Many2many(
        'ir.attachment', "cms_project_attachment_rel", string='Attachments')

    state = fields.Selection([('draft', 'Draft'), ('turn in', 'Turned In')], 'State', default="draft")

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'turn in'),
                   ('turn in', 'draft')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for r in self:
            if r.is_allowed_transition(r.state, new_state):
                r.state = new_state
            else:
                # continue
                # displaying a custom error message
                msg = _('Moving from %s to %s is not allowed') % (
                    r.state, new_state)
                raise UserError(msg)

    def make_draft(self):
        self.change_state('draft')

    def make_turn_in(self):
        self.change_state('turn in')

    _sql_constraints = [
        ('assignment_id', 'UNIQUE(assignment_id)',
         'Assignment ID should be Unique.')]


class CMSAssignmentEvaluation(models.Model):
    _name = "cms.assignmentevaluation"
    _description = "Evaluation of Assignment"

    assignment_id = fields.Many2one('cms.assignment', 'Assignment ID')
    staff_name = fields.Many2one('cms.staff', 'Staff')
    department = fields.Many2one('cms.department', 'Department')
    marks_title = fields.Selection(
        [('assign1', 'Assignment 1'), ('assign2', 'Assignment 2'), ('assign3', "Assignment 3"), ('assign4', 'Assignment 4')], 'Title')
    marks_val = fields.Integer(string="Marks Value")
    date = fields.Date(string='Date')
    remark = fields.Text('Remark')
    child_evaluations = fields.One2many(
        'cms.assignmentevaluation', 'parent_id', string='Assignment Evaluations')
    parent_id = fields.Many2one(
        'cms.assignmentevaluation', string='Assignment Evaluation')


class CMSStudent(models.Model):

    _name = 'cms.student'                # Internal name of a model
    _description = 'Student Information'

    name = fields.Char('Student Name', required=True)
    rollno = fields.Char("Roll No", required=True)
    father_name = fields.Char('Father Name', required=True)
    admission_no = fields.Char(string='Admission No.', readonly=True)
    registration_no = fields.Char(string='Registration No.')
    admission_date = fields.Datetime('Admission Date', default=date.today())
    birth_date = fields.Date('Date of Birth')
    cnic = fields.Char(string='CNIC')
    phone = fields.Char('Phone no.')
    email = fields.Char('Email')
    cgpa = fields.Float('CGPA')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], 'Gender', required=True)
    active = fields.Boolean(default=True, help='Help here')
    image = fields.Binary('Image', widget="image",
                          options={'size': (500, 500)})
    department_id = fields.Many2one('cms.department', 'Department')
    remark = fields.Text('Remark')
    age = fields.Integer(compute='_compute_student_age',
                         string='Age (Years)', readonly=True)

    _sql_constraints = [
        ('rollno', 'UNIQUE(rollno)',
         'Roll No. should be Unique.'),
        ('admisson_unique', 'UNIQUE(admission_no)',
         'Student Admission No. should be Unique.'),
        ('email_check', "CHECK(position('@' in email) > 0)",
         "Email address must contain '@' symbol")]

    @api.constrains('cnic')
    def _check_cnic_formate(self):
        for rec in self:
            if rec.cnic:
                cnic = str(rec.cnic).strip().replace("-", "")
                if cnic:
                    if len(cnic) != 13:
                        raise ValidationError(
                            _('''Student CNIC should be 13 digits!'''))
                    if not cnic.isdecimal():
                        raise ValidationError(
                            _('''Student CNIC should have valid characters!'''))

    @api.depends('birth_date')
    def _compute_student_age(self):
        '''Method to calculate student age'''
        for rec in self:
            rec.age = 0
            if rec.birth_date:
                today = date.today()
                years = today.year - rec.birth_date.year - \
                    ((today.month, today.day) <
                     (rec.birth_date.month, rec.birth_date.day))
                rec.age = years

        if self.admission_date:
            year = self.admission_date.year
        else:
            raise ValidationError(
                _('Please enter admission date for student %s)', self.name))


class CMSStaff(models.Model):

    _name = 'cms.staff' 
    _description = 'staff Information'

    name = fields.Char('Staff Name', required=True)
    cnic = fields.Char(string='CNIC')
    father_name = fields.Char('Father Name', required=True)
    admission_no = fields.Char(string='Admission No.')
    admission_date = fields.Datetime('Admission Date', default=date.today())
    birth_date = fields.Date('Date of Birth')
    phone = fields.Char('Phone no.')
    email = fields.Char('Email')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], 'Gender', required=True)
    active = fields.Boolean(default=True, help='Help here')
    image = fields.Binary('Image', widget="image",
                          options={'size': (500, 500)})
    department_id = fields.Many2one('cms.department', 'Department')
    remark = fields.Text('Remark')
    age = fields.Integer(compute='_compute_staff_age',
                         string='Age (Years)', readonly=True)

    parent_id = fields.Many2one(
        'cms.staff', string='Main Staff', ondelete='restrict', index=True)

    @api.depends('parent_id.parent_path')
    def _compute_parent_path(self):
        for record in self:
            if record.parent_id:
                record.parent_path = '%s/%s' % (
                    record.parent_id.parent_path, record.parent_id.name)
            else:
                record.parent_path = record.name

    _sql_constraints = [
        ('admisson_unique', 'UNIQUE(admission_no)',
         'Staff Admission No. should be Unique.'),
        ('email_check', "CHECK(position('@' in email) > 0)",
         "Email address must contain '@' symbol")]

    @api.constrains('cnic')
    def _check_cnic_formate(self):
        for rec in self:
            if rec.cnic:
                cnic = str(rec.cnic).strip().replace("-", "")
                if cnic:
                    if len(cnic) != 13:
                        raise ValidationError(
                            _('''Staff CNIC should be 13 digits!'''))
                    if not cnic.isdecimal():
                        raise ValidationError(
                            _('''Staff CNIC should have valid characters!'''))

    @api.depends('birth_date')
    def _compute_staff_age(self):
        '''Method to calculate staff age'''
        for rec in self:
            rec.age = 0
            if rec.birth_date:
                today = date.today()
                years = today.year - rec.birth_date.year - \
                    ((today.month, today.day) <
                     (rec.birth_date.month, rec.birth_date.day))
                rec.age = years
