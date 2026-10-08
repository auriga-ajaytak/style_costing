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
- **Reports** — Style Costing Summary; Fabric and Trim Consumption; BOM Costing
  Reconciliation; Style Order Tracking.
- **Role profiles** — Style Merchandiser, Style Costing Manager and Style
  Production Planner, each with the ERPNext roles it needs.
- **Number cards** on the Styling workspace, and a user guide in `docs/`.
- **BOM generation** — Create → BOMs on a Style Master drafts an ERPNext BOM for
  each garment Item linked to the style.
- **Buyer Cost Sheet** print format — buyer columns only.
- **Dashboard charts** on the Styling workspace — styles by buyer, season and
  merchandiser.
- **Notifications** — to Costing Managers when a style is marked Costed, and to
  its owner when it is approved (in-app, with the approval workflow on).
- **Onboarding** — a four-step checklist, and a warning on the settings page
  when Item Groups have no Group Category.
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

- **Style Name is now an Item and Style Category its Item Group.** The Product
  and Product Category masters, which duplicated them, are removed. Saving a
  style links its Item and that item's variants back to it.
- Opening a Style Master as any user other than Administrator failed with
  "Insufficient Permission for Trims Process Route"; fixed.

### Not changed
- No costing calculation has been altered since the v16 port.

## 0.0.1

- Port of the v13 style master add-on to Frappe v16 / ERPNext v16. See the
  README for the port notes.
