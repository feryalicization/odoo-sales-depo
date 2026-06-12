# Sales Depo Management

Phase 2 of the `sales_depo_management` module introduces only the sales master
data foundation for Odoo 18 and Phase 3 adds assignment and access features:

- `sales.region`
- `sales.depo`
- user-to-depo assignment
- customer default depo
- region/depo access groups and record rules
- sales configuration menus, actions, and views
- manager security group and ACLs
- model constraints and archive-first delete behavior

This phase does not yet implement:

- sales order customization
- reporting
- approval workflow

## Installation

1. Ensure `custom-addons` is present in `addons_path`.
2. Update the Apps list in Odoo.
3. Install `Sales Depo Management`.

CLI example:

```bash
./.venv/bin/python odoo/odoo-bin -c config/odoo.conf -d odoo_sales_depo -i sales_depo_management --stop-after-init
```

## Security

Phase 2 adds a dedicated group:

- `Sales Depo Master Manager`

This group implies Odoo's Sales Manager group so its menus can live under
`Sales / Configuration`. Assign this group to users who should manage regions
and depos.

## Manual validation

1. Open `Sales / Configuration / Sales Depo / Regions`.
2. Create regions with unique codes per company.
3. Open `Sales / Configuration / Sales Depo Management / Depos`.
4. Create depos linked to regions and warehouses in the same company.
5. Open `Settings / Users & Companies / Users` and assign `Depo Assignments`.
6. Open a customer contact and set `Default Depo`.
7. Test access with a user in `Sales Depo User`, `Depo Supervisor`, or `Regional Manager`.
8. Archive a region or depo and verify it disappears from default searches.
9. Try deleting an active region or depo and confirm the module asks you to archive first.
