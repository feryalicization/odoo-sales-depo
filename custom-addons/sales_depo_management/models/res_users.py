from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    depo_ids = fields.Many2many(
        "sales.depo",
        "sales_depo_user_rel",
        "user_id",
        "depo_id",
        string="Assigned Depos",
        domain="[('active', '=', True), ('company_id', 'in', company_ids)]",
    )
    default_depo_id = fields.Many2one(
        "sales.depo",
        string="Default Depo",
        domain="[('id', 'in', depo_ids), ('active', '=', True)]",
    )

    @api.constrains("depo_ids", "default_depo_id", "company_ids")
    def _check_depo_assignments(self):
        for user in self:
            invalid_depos = user.depo_ids.filtered(
                lambda depo: depo.company_id not in user.company_ids
            )
            if invalid_depos:
                raise ValidationError(
                    _(
                        "Assigned depos must belong to one of the user's allowed companies."
                    )
                )
            if user.default_depo_id and user.default_depo_id not in user.depo_ids:
                raise ValidationError(
                    _("The default depo must be included in the assigned depos.")
                )
            if user.default_depo_id and user.default_depo_id.company_id not in user.company_ids:
                raise ValidationError(
                    _(
                        "The default depo must belong to one of the user's allowed companies."
                    )
                )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["depo_ids", "default_depo_id"]
