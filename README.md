# Odoo Sales Management per Depo

Custom Odoo 18 Community module for managing sales orders per depo.

## Technology

- Odoo 18 Community
- Python 3.11
- PostgreSQL 17

## Project structure

- `custom-addons/` — custom Odoo modules
- `config/odoo.conf.example` — example configuration
- `odoo/` — local Odoo source, excluded from Git
- `.venv/` — local Python virtual environment, excluded from Git

## Run locally

```bash
source .venv/bin/activate
python odoo/odoo-bin -c config/odoo.conf
