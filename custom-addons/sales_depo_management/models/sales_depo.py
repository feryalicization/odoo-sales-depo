from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SalesDepo(models.Model):
    _name = "sales.depo"
    _description = "Sales Depo"
    _order = "company_id, name, id"
    _check_company_auto = True

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)
    region_id = fields.Many2one(
        "sales.region",
        required=True,
        check_company=True,
        domain="[('active', '=', True), ('company_id', '=', company_id)]",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        readonly=True,
        index=True,
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        check_company=True,
        domain="[('active', '=', True), ('company_id', '=', company_id)]",
    )
    manager_id = fields.Many2one(
        "res.users",
        string="Manager",
        domain="[('share', '=', False), ('company_ids', 'in', company_id)]",
    )
    user_ids = fields.Many2many(
        "res.users",
        "sales_depo_user_rel",
        "depo_id",
        "user_id",
        string="Assigned Users",
        domain="[('share', '=', False), ('company_ids', 'in', company_id)]",
    )
    address = fields.Text()
    phone = fields.Char()
    email = fields.Char()
    description = fields.Text()

    _sql_constraints = [
        (
            "sales_depo_code_company_uniq",
            "unique(company_id, code)",
            "The depo code must be unique per company.",
        ),
    ]

    @staticmethod
    def _normalize_code(code):
        return (code or "").strip().upper()

    @api.onchange("region_id")
    def _onchange_region_id(self):
        for depo in self:
            depo.company_id = depo.region_id.company_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "code" in vals:
                vals["code"] = self._normalize_code(vals["code"])
            if vals.get("region_id"):
                region = self.env["sales.region"].browse(vals["region_id"])
                vals["company_id"] = region.company_id.id
        return super().create(vals_list)

    def write(self, vals):
        if "code" in vals:
            vals["code"] = self._normalize_code(vals["code"])
        if vals.get("region_id"):
            region = self.env["sales.region"].browse(vals["region_id"])
            vals["company_id"] = region.company_id.id
        return super().write(vals)

    @api.constrains("region_id", "company_id")
    def _check_region_company(self):
        for depo in self:
            if depo.region_id and depo.company_id != depo.region_id.company_id:
                raise ValidationError(
                    _("The depo company must match the selected region company.")
                )

    @api.constrains("warehouse_id", "company_id")
    def _check_warehouse_company(self):
        for depo in self.filtered("warehouse_id"):
            if depo.warehouse_id.company_id != depo.company_id:
                raise ValidationError(
                    _("The warehouse company must match the depo company.")
                )

    @api.constrains("manager_id", "user_ids", "company_id")
    def _check_user_companies(self):
        for depo in self:
            if depo.manager_id and depo.company_id not in depo.manager_id.company_ids:
                raise ValidationError(
                    _("The depo manager must belong to the depo company.")
                )
            invalid_users = depo.user_ids.filtered(
                lambda user: depo.company_id not in user.company_ids
            )
            if invalid_users:
                raise ValidationError(
                    _(
                        "All assigned depo users must belong to the depo company."
                    )
                )

    def unlink(self):
        active_records = self.filtered("active")
        if active_records:
            raise UserError(
                _(
                    "You cannot delete active depos. Archive them first to avoid unsafe data removal."
                )
            )
        return super().unlink()
