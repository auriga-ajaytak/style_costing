# Style Costing

Costing for garment manufacturers and exporters, inside ERPNext.

A garment factory does not quote a product, it quotes a **style**: one design,
for one buyer, in one season, with its own fabric and trim bill, sewing
operations and margin. The quote goes out before any order exists. ERPNext has
no place to build that quote. This app adds it.

| You get | |
|---|---|
| **Style Master** | One document per style: buyer and style details, tech pack, fabric and trims, process routes, marker, SMV, value addition, time and action, lab tests |
| **Costing sheet** | Per-piece cost built up from fabric, trims, manufacturing and other costs, against a sales price target, with a five-step markup ladder |
| **Buyer view** | Company cost and buyer cost side by side on every row, and a *Buyer Cost Sheet* print that shows the buyer's side only |
| **Approval** | An optional Draft → Costed → Approved → Quoted workflow, with notifications |
| **Style to order** | Quote styles on a Quotation, trace Sales Order lines back to their style, and draft ERPNext BOMs from a style |
| **Reports** | Costing summary and margin, fabric and trim consumption, BOM-versus-costing reconciliation, order tracking |
| **Setup help** | A settings page, role profiles, an onboarding checklist and removable demo data |

**New here? Read the [user guide](docs/user-guide.md).** It covers setup and a
complete style, start to finish, in plain language.

The rest of this page is for whoever installs and maintains the app.

## Requirements

| | |
|---|---|
| Frappe | v16 (`version-16`) |
| ERPNext | v16 (`version-16`) — declared via `required_apps` |
| Python | ≥ 3.14 (Frappe v16 requirement) |
| Node | ≥ 24 |
| MariaDB | ≥ 10.6 |

## Install

```bash
bench get-app https://github.com/auriga-ajaytak/style_costing.git
bench --site <site> install-app style_costing
bench build --app style_costing
```

Then open the **Styling** workspace and follow
[Set up](docs/user-guide.md#1-set-up-once) in the user guide. The one step that
cannot be skipped on a site with existing items is tagging Item Groups with a
Group Category.

## What the app adds

**60 DocTypes.** Style Master is the only one most users open; it is
submittable and carries 112 fields across 10 tabs. Around 25 are masters
(seasons, segments, cost heads, lab tests, ...), one is the settings page, and
the rest are the child tables behind Style Master's grids. Six masters ship
with generic default records.

**Style Costing Settings** — the style naming series, the defaults a new style
starts from (style rate, efficiency, cost heads), whether this app names Items,
the approval workflow switch, and demo data. It also warns about anything that
still needs setting up.

**Roles and role profiles** — Costing Manager, Merchandiser and Production
Planner. Only a Costing Manager can submit a style. The matching role profiles
(Style Costing Manager, Style Merchandiser, Style Production Planner) add the
ERPNext roles each person needs for items, buyers, quotations and BOMs.

**Costing approval workflow** — off by default. Switched on in the settings, it
runs Draft → Costed → Approved → Quoted and replaces Submit and Cancel on Style
Master. Costing Managers are notified when a style is marked Costed; its owner
when it is approved.

**BOM generation** — *Create → BOMs* on a Style Master drafts an ERPNext BOM for
the style's garment Item: each of its variants when it is a template, or the
item itself when it has none. The per-garment quantity is
the row's consumption (for trims, times pieces per garment), without extras,
wastage or samples. Running it again refreshes the drafts; an item that already
has a submitted BOM is left alone.

**Reports** — *Style Costing Summary*, *Fabric and Trim Consumption*,
*BOM Costing Reconciliation* and *Style Order Tracking*. All read stored values.

**Print formats** — *Style Costing Sheet* (internal) and *Buyer Cost Sheet*
(buyer columns only).

**Workspace** — "Styling": number cards, charts of styles by buyer, season and
merchandiser, and links to every document, master and report.

**Item extensions** — 51 custom fields and 16 property setters covering fabric
construction, GSM, composition, weave, trims attributes, item references and a
generated QR code, plus custom fields on Brand, Item Group, Item Barcode and
Item Supplier.

**Style ↔ Item link** — a style is costed for a garment Item: *Style Name* on
Style Master is a link to Item (garment groups only, templates rather than
variants), and *Style Category* is that item's Item Group. Saving the style
sets `Item.style_master` on the item and its variants, and
`Sales Order Item.style_master` fetches it from `item_code`, so an order line
traces back to its style without duplicate entry. An item keeps the first
style costed for it; an amended style takes over from the one it replaces.
v13 used two masters of its own here, Product and Product Category, which
duplicated Item and Item Group and have been removed.

**Item naming override** — `StyleItem` derives the item code series from
`Item Group.group_category`: `F-` fabric, `T-` trims, `G-` garment, `Y-` yarn,
`CG-` capital goods, `C-` consumables, `S-` stationery, `I-` otherwise.

## Layout

```
style_costing/
├── queries.py                      whitelisted link queries + meta helper
├── docevents/                      Item class override, Item/Quotation hooks
├── public/js/
│   ├── style_form.js               Style Master client-side form logic
│   ├── style_costing.bundle.js
│   ├── item.js, item_list.js, quotation.js
├── fixtures/                       structural defaults (cost heads, seasons, segments, ...)
├── approval.py                     the optional approval workflow
├── bom.py                          BOM generation from a style
├── setup.py                        install hooks, role profiles, setup warnings
├── demo/                           sample records, installed from the settings page
├── patches/                        migration patches
└── style_costing/
    ├── custom/                     Customize Form exports (Item, Brand, ...)
    ├── doctype/                    60 DocTypes
    ├── report/                     4 script reports
    ├── print_format/               Style Costing Sheet, Buyer Cost Sheet
    ├── dashboard_chart/, number_card/
    ├── notification/               approval notifications
    ├── module_onboarding/, onboarding_step/
    └── workspace/styling/          the "Styling" workspace
```

## Notes on the v13 → v16 port

The app was ported from `cmv_erp_style_master_addon` (Frappe/ERPNext v13) and is
modelled on the style costing module of Visual Gems ERP.

### Framework changes handled

| v13 | v16 |
|---|---|
| `setup.py` + `requirements.txt` | `pyproject.toml` (flit) |
| `config/desktop.py`, `config/docs.py` | removed — module comes from `modules.txt` + Workspace |
| `app_version`, `app_color`, `app_icon` in `hooks.py` | removed |
| Desk route `/app/...` | `/desk/...` |
| `name_case` on DocType | removed |
| `Order Type` DocType (ERPNext) | removed — now a Select on Quotation / Sales Order |
| `gst_hsn_code` → Link "GST HSN Code" | GST moved to `india_compliance`; field is now Data |
| `hub_sync_id` and Hub property setters | removed with Frappe Hub |
| Quotation `subscription_section`, `more_info` | `auto_repeat_section`, `more_info_tab` |

### Deliberate changes

**One style DocType instead of two.** v13 shipped a second DocType, **Style Costing**, that duplicated Style
Master field-for-field — the same 110 fields with identical properties, the same
client script, the same costing template. Nothing referenced it: Quotation,
Operation Bulletin, Design and Marker, the print format and the dashboard all
point at Style Master. It was dropped, and its (correct) tab layout was moved
onto Style Master, whose own `field_order` had drifted — Buyer, Style Name and
Series had ended up under Value Addition while the Style Details and Logistics
sections rendered empty.

**Native tabs.** v13 layered a ~160-line jQuery overlay (`setupTabView`) on top
of Section Breaks to fake tabs — it rewrote DOM classes, hid sections by hand and
re-rendered fields on every tab click. The DocTypes now use real `Tab Break`
fields and the overlay is gone.

**One implementation instead of three.** v13 carried the same logic in
`style_master.js` (1,900 lines), `fabric/fabric.js` (913 lines, layered onto
Style Master through `doctype_js`) and `style_costing.js` (2,716 lines —
the union of the first two). All three are now `public/js/style_form.js`, which
both DocTypes register.

**Child handlers register once.** v13 called `frappe.ui.form.on()` for the 12
child DocTypes from inside the parent's `onload`, so a new copy of every handler
was added on each form load. They now register a single time.

**Parameterised SQL.** `saveProcessRoute` (fabric and trims), the merchandiser
and item link queries, and the lab-testing-template query all built SQL with
`str.format` or `+` on client-supplied values. They now use the query builder,
and `saveProcessRoute` validates the parent document and its permissions and
only writes fields that exist on the child DocType.

**Live metadata.** `get_doc_wise_columns` read the DocType's JSON file straight
off disk, so Customize Form changes never reached the datatable. It now returns
`frappe.get_meta(...)`.

### Bugs fixed in passing

* `Style Costing` had two `amended_from` fields, the surviving one
  pointing at `Style Master`; amending produced a link to the wrong DocType.
* The module name was split across `"CMV ERP Style Master Addon"` (51 DocTypes)
  and `"Cmv Erp Style Master Addon"` (11); `modules.txt` declared only the
  second. Everything is now one module.
* `doctype_js` mapped `"Style Master"` to `doctype/fabric/fabric.js` — a file
  named after an unrelated child DocType. That code is now in `style_form.js`.
* `quotation.js` read `cur_frm.fields_dict.items.grid` unguarded. Its own first
  run hides `items`, so the next refresh threw
  `Cannot read properties of undefined (reading 'grid')`.
* The `styles` custom field on Quotation, which `quotation.js` and the
  `Quotation Style Master` child table both depend on, was never committed — it
  existed only on the client's site. It ships in `custom/quotation.json` now.
* A stray `console.log` on every fabric/trim cell edit.

### Not carried over

The v13 `fixtures/workspace.json` was a 432 KB dump of **all 34 workspaces on
the source site** — Accounting, HR, Healthcare, Education and the rest.
Installing it would overwrite the standard ERPNext workspaces. Only this app's
own workspace was ported, rebuilt as `workspace/styling` in the v16 `content`
format.

`fixtures/custom_field.json` duplicated the Item fields already in
`custom/item.json` and was dropped in favour of the Customize Form export.

The `stock_custom` workspace ("Stock-Custom", `extends: Stock`) was a
link-for-link copy of the v13 standard Stock workspace and added nothing, so it
was not carried over.

## Things to know

**Every Item gets a generated code.** The `StyleItem` override replaces
`item_code` on *every* Item, even when one is typed in — this is v13 behaviour,
kept as the default. Tick **Keep ERPNext Item Codes** in Style Costing Settings
to turn it off. It means an Item cannot be created with a chosen code while this app
is installed, so data imports that rely on specific item codes, and ERPNext's own
shared test records (`_Test Item` and friends), do not work unchanged. The app's
test suite opts out of those shared records for this reason.

**Do not name a Workspace after a DocType.** The v16 desk resolves
`/desk/<slug>/...` to a Workspace before a DocType, so a workspace named after a
style form would shadow that form. The workspace is called "Styling", as it was
in v13.

## Tests

```bash
bench --site <site> run-tests --app style_costing
```

`tests/test_style_master.py` holds 34 integration tests: item codes and the QR
hook, the Style Master lifecycle and tab structure, every whitelisted link
query, process routes, the settings, roles, the approval workflow, BOM
generation and reconciliation, the reports, the buyer print format, demo data
and the Item override check. They run on every push through GitHub Actions.

The costing arithmetic itself runs in the browser (`public/js/style_form.js`)
and is not covered by these tests.

## License

GNU General Public License v3.0 — see [license.txt](license.txt). The same
licence as ERPNext, which this app extends.
