# Changelog

All notable changes to Style Costing. Versions follow [Semantic Versioning](https://semver.org/).

## Unreleased

### Added
- **Style Costing Settings** — naming series, default style rate, default
  efficiency, default cost heads, Keep ERPNext Item Codes, and the costing
  approval workflow switch.
- **Roles** — Costing Manager, Merchandiser and Production Planner, with
  permissions on every DocType. Only a Costing Manager can submit a style.
- **Costing approval workflow** (optional) — Draft → Costed → Approved → Quoted.
- **Reports** — Style Costing Summary; Fabric and Trim Consumption.
- **Buyer Cost Sheet** print format — buyer columns only.
- **Demo data** — sample masters installed and removed from the settings page.
- `company` on Style Master; change tracking on Style Master and Operation Bulletin.
- A warning when another app also overrides the Item controller.
- CI running the test suite on Frappe and ERPNext v16.

### Changed
- Licence is GPL-3.0 (was declared MIT, with no licence text).
- Style Master is numbered `STY-.YYYY.-.####` (was `CMV-STYLE-.YYYY.-`).
- The Merchandiser fixture is no longer installed. Season `Autmn` is `Autumn`
  and Cost Head `GARMENT REJECTION` is `Garment Rejection`; existing sites are
  renamed by a patch.

### Not changed
- No costing calculation has been altered since the v16 port.

## 0.0.1

- Port of the v13 style master add-on to Frappe v16 / ERPNext v16. See the
  README for the port notes.
