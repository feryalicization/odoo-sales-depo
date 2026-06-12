from psycopg2 import IntegrityError

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestSalesRegionDepo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.other_company = cls.env["res.company"].create(
            {
                "name": "Sales Depo Test Branch",
                "partner_id": cls.env["res.partner"].create(
                    {"name": "Sales Depo Test Branch"}
                ).id,
                "currency_id": cls.company.currency_id.id,
            }
        )
        cls.region = cls.env["sales.region"].create(
            {
                "name": "West Java",
                "code": "wjt1",
                "company_id": cls.company.id,
            }
        )
        cls.other_region = cls.env["sales.region"].create(
            {
                "name": "Central Java",
                "code": "cjt1",
                "company_id": cls.other_company.id,
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)],
            limit=1,
        )
        cls.other_warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test Branch Warehouse",
                "code": "TBW",
                "company_id": cls.other_company.id,
            }
        )

    def test_region_code_is_normalized(self):
        self.assertEqual(self.region.code, "WJT1")

    def test_region_code_unique_per_company(self):
        with self.cr.savepoint(), mute_logger("odoo.sql_db"):
            with self.assertRaises(IntegrityError):
                self.env["sales.region"].create(
                    {
                        "name": "Duplicate Region",
                        "code": "wjt1",
                        "company_id": self.company.id,
                    }
                )

    def test_depo_creation(self):
        depo = self.env["sales.depo"].create(
            {
                "name": "Bandung",
                "code": "bdt1",
                "region_id": self.region.id,
                "warehouse_id": self.warehouse.id,
            }
        )
        self.assertEqual(depo.code, "BDT1")
        self.assertEqual(depo.company_id, self.region.company_id)

    def test_depo_code_unique_per_company(self):
        self.env["sales.depo"].create(
            {
                "name": "Bandung",
                "code": "bdt2",
                "region_id": self.region.id,
            }
        )
        with self.cr.savepoint(), mute_logger("odoo.sql_db"):
            with self.assertRaises(IntegrityError):
                self.env["sales.depo"].create(
                    {
                        "name": "Cimahi",
                        "code": "BDT2",
                        "region_id": self.region.id,
                    }
                )

    def test_warehouse_company_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["sales.depo"].create(
                {
                    "name": "Cross Company Depo",
                    "code": "CCD",
                    "region_id": self.region.id,
                    "warehouse_id": self.other_warehouse.id,
                }
            )

    def test_active_records_must_be_archived_before_delete(self):
        region = self.env["sales.region"].create(
            {
                "name": "Delete Guard Region",
                "code": "DGR",
                "company_id": self.company.id,
            }
        )
        depo = self.env["sales.depo"].create(
            {
                "name": "Delete Guard Depo",
                "code": "DGD",
                "region_id": self.region.id,
            }
        )
        with self.assertRaises(UserError):
            region.unlink()
        with self.assertRaises(UserError):
            depo.unlink()
