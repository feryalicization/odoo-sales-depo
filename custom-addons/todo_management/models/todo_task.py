from odoo import fields, models


class TodoTask(models.Model):
    _name = "todo.task"
    _description = "To-Do Task"
    _order = "priority desc, date_deadline asc, id desc"
    _check_company_auto = True

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Urgent"),
        ],
        default="1",
        required=True,
    )
    state = fields.Selection(
        [
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="todo",
        required=True,
    )
    date_deadline = fields.Date()
    user_id = fields.Many2one(
        "res.users",
        string="Assigned To",
        default=lambda self: self.env.user,
        check_company=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
