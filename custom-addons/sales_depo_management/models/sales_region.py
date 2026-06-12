from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SalesRegion(models.Model):
    _name = "sales.region"
    _description = "Sales Region"
    _order = "company_id, name, id"
    _check_company_auto = True

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    manager_id = fields.Many2one(
        "res.users",
        string="Manager",
        domain="[('share', '=', False), ('company_ids', 'in', company_id)]",
    )
    depo_ids = fields.One2many("sales.depo", "region_id", string="Depos")
    description = fields.Text()

    _sql_constraints = [
        (
            "sales_region_code_company_uniq",
            "unique(company_id, code)",
            "The region code must be unique per company.",
        ),
    ]

    @staticmethod
    def _normalize_code(code):
        return (code or "").strip().upper()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "code" in vals:
                vals["code"] = self._normalize_code(vals["code"])
        return super().create(vals_list)

    def write(self, vals):
        if "code" in vals:
            vals["code"] = self._normalize_code(vals["code"])
        return super().write(vals)

    @api.constrains("manager_id", "company_id")
    def _check_manager_company(self):
        for region in self.filtered("manager_id"):
            if region.company_id not in region.manager_id.company_ids:
                raise ValidationError(
                    _("The region manager must belong to the region company.")
                )

    def unlink(self):
        active_records = self.filtered("active")
        if active_records:
            raise UserError(
                _(
                    "You cannot delete active regions. Archive them first to avoid unsafe data removal."
                )
            )
        return super().unlink()
