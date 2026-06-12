from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_depo_id = fields.Many2one(
        "sales.depo",
        string="Default Depo",
        domain="[('active', '=', True)]",
    )
    region_id = fields.Many2one(
        "sales.region",
        string="Sales Region",
        related="default_depo_id.region_id",
        store=True,
        readonly=True,
    )

    @api.constrains("default_depo_id", "company_id")
    def _check_default_depo(self):
        for partner in self.filtered("default_depo_id"):
            if not partner.default_depo_id.active:
                raise ValidationError(_("Only active depos can be assigned to customers."))
            if partner.company_id and partner.default_depo_id.company_id != partner.company_id:
                raise ValidationError(
                    _("The customer default depo must match the partner company.")
                )
