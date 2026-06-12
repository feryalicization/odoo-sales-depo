from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSalesDepoPhase3(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.other_company = cls.env["res.company"].create(
            {
                "name": "Sales Depo Phase 3 Branch",
                "partner_id": cls.env["res.partner"].create(
                    {"name": "Sales Depo Phase 3 Branch"}
                ).id,
                "currency_id": cls.company.currency_id.id,
            }
        )
        cls.region_main = cls.env["sales.region"].create(
            {
                "name": "West Java",
                "code": "WJ3",
                "company_id": cls.company.id,
            }
        )
        cls.region_other = cls.env["sales.region"].create(
            {
                "name": "Central Java",
                "code": "CJ3",
                "company_id": cls.other_company.id,
            }
        )
        cls.depo_main = cls.env["sales.depo"].create(
            {
                "name": "Bandung",
                "code": "BD3",
                "region_id": cls.region_main.id,
            }
        )
        cls.depo_other = cls.env["sales.depo"].create(
            {
                "name": "Semarang",
                "code": "SM3",
                "region_id": cls.region_other.id,
            }
        )
        cls.group_user = cls.env.ref("sales_depo_management.group_sales_depo_user")
        cls.group_supervisor = cls.env.ref("sales_depo_management.group_sales_depo_supervisor")
        cls.group_region_manager = cls.env.ref(
            "sales_depo_management.group_sales_depo_region_manager"
        )
        cls.group_master_manager = cls.env.ref(
            "sales_depo_management.group_sales_depo_master_manager"
        )

    def _create_internal_user(self, name, login, groups, company_ids=None, company_id=None):
        allowed_companies = company_ids or self.company
        return self.env["res.users"].with_context(no_reset_password=True).create(
            {
                "name": name,
                "login": login,
                "email": login,
                "company_id": (company_id or self.company).id,
                "company_ids": [(6, 0, allowed_companies.ids)],
                "groups_id": [(6, 0, groups.ids)],
            }
        )

    def _model_with_user(self, model_name, user):
        return self.env[model_name].with_user(user).with_context(
            allowed_company_ids=user.company_ids.ids
        )

    def test_user_default_depo_must_be_assigned(self):
        user = self._create_internal_user(
            "Depo User A",
            "depo.user.a@example.com",
            self.group_user,
        )
        with self.assertRaises(ValidationError):
            user.write({"default_depo_id": self.depo_main.id})

    def test_user_depo_company_must_be_allowed(self):
        user = self._create_internal_user(
            "Depo User B",
            "depo.user.b@example.com",
            self.group_user,
        )
        with self.assertRaises(ValidationError):
            user.write({"depo_ids": [(4, self.depo_other.id)]})

    def test_partner_default_depo_sets_region(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Customer West Java",
                "company_id": self.company.id,
                "default_depo_id": self.depo_main.id,
            }
        )
        self.assertEqual(partner.region_id, self.region_main)

    def test_partner_company_must_match_default_depo(self):
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(
                {
                    "name": "Wrong Customer",
                    "company_id": self.company.id,
                    "default_depo_id": self.depo_other.id,
                }
            )

    def test_sales_depo_user_only_sees_assigned_records(self):
        user = self._create_internal_user(
            "Assigned User",
            "assigned.user@example.com",
            self.group_user,
        )
        user.write({"depo_ids": [(4, self.depo_main.id)]})
        self.assertEqual(
            self._model_with_user("sales.depo", user).search_count(
                [("id", "in", [self.depo_main.id, self.depo_other.id])]
            ),
            1,
        )
        self.assertEqual(
            self._model_with_user("sales.region", user).search_count(
                [("id", "in", [self.region_main.id, self.region_other.id])]
            ),
            1,
        )

    def test_regional_manager_sees_managed_region_and_depos(self):
        user = self._create_internal_user(
            "Regional Manager User",
            "regional.manager@example.com",
            self.group_region_manager,
        )
        self.region_main.write({"manager_id": user.id})
        self.assertEqual(
            self._model_with_user("sales.region", user).search_count(
                [("id", "in", [self.region_main.id, self.region_other.id])]
            ),
            1,
        )
        self.assertEqual(
            self._model_with_user("sales.depo", user).search_count(
                [("id", "in", [self.depo_main.id, self.depo_other.id])]
            ),
            1,
        )

    def test_master_manager_sees_all_company_records(self):
        user = self._create_internal_user(
            "Depo Master Manager",
            "depo.master.manager@example.com",
            self.group_master_manager,
        )
        self.assertEqual(
            self._model_with_user("sales.region", user).search_count(
                [("id", "in", [self.region_main.id, self.region_other.id])]
            ),
            1,
        )
        self.assertEqual(
            self._model_with_user("sales.depo", user).search_count(
                [("id", "in", [self.depo_main.id, self.depo_other.id])]
            ),
            1,
        )
        self.assertEqual(
            self._model_with_user("sales.region", user).search_count(
                [("company_id", "=", self.other_company.id)]
            ),
            0,
        )
        self.assertEqual(
            self._model_with_user("sales.depo", user).search_count(
                [("company_id", "=", self.other_company.id)]
            ),
            0,
        )
