# Style Costing — Product Plan

A plan for developing `style_costing` from a single-client customisation
into a **generic, publicly distributable ERPNext module for the apparel
industry**.

| | |
|---|---|
| App | `style_costing` |
| Module | Style Costing |
| Repo | `github.com/auriga-ajaytak/style_costing` |
| Current version | 0.0.1 (unreleased work on `main`, see CHANGELOG.md) |
| Platform | Frappe v16 · ERPNext v16 · Python ≥ 3.14 |
| Dependency | ERPNext (`required_apps = ["erpnext"]`) |
| Scale | 60 DocTypes · 4 reports · 2 print formats · 3,745 lines client JS · 34 integration tests |
| Target | Public release — any garment exporter or CMT manufacturer on ERPNext |

### Status at a glance — 2026-10-07

| Phase | State |
|---|---|
| 0 — Installable | ✅ Done. Not yet proven on a fresh site. |
| 1 — Correct | Company field and Item override handling done. Everything that changes a computed number is **parked** (§8.1). |
| 2 — A product | ✅ Roles, role profiles, permissions, change tracking, approval workflow, onboarding. Buyer role **deferred**. |
| 3 — Defensible | Reports, charts, BOM generation and reconciliation done. Server-side costing **parked**; costing versions **deferred**. |
| 4 — Sellable | Buyer cost sheet, CI, changelog, user guide, demo data done. Quantity breaks and the importer **parked**. |

**Parked** means it changes costing arithmetic and waits for the product owner
to test the module and ask for it. **Deferred** means the product owner has
chosen to build it later: costing versions, the buyer role, the tech pack
print format, variant-specific BOMs and all Operation Bulletin work.

**Next:** the product owner tests the whole module on a clean site, then
calculation changes are taken one at a time.

---

## 1. The product

### 1.1 The problem

Apparel manufacturers do not cost a *product*. They cost a **style** — a garment
design, for one buyer, in one season, across a size range, with its own fabric
and trim bill, its own sewing operations, and its own margin ladder. The quote
goes out **before any order exists**, and it has to survive line-by-line
scrutiny when the buyer pushes back.

ERPNext cannot express this. Its BOM is a manufacturing bill priced from
valuation rates. It has no concept of:

- consumption + purchase extra + production extra + wastage
- *our cost* and *buyer cost* running side by side on the same row
- sewing cost derived as `SMV × style rate ÷ line efficiency`
- a cost head charged as a percentage of *total raw material + manufacturing*
- local vs. import split of fabric and trims in the cost summary
- a style quoted at five markup levels before an order exists

### 1.2 Where the module sits

```
Buyer enquiry
    ↓
Style Master ─── fabric + trims BOM, process routes, SMV, value addition,
    │            time & action, lab tests  →  per-piece costing sheet
    │                                          + sales price markup ladder
    ↓
Quotation ─────── quotes styles, not items
    ↓
Sales Order ───── order line traces back to the style it was costed from
    ↓
Operation Bulletin ─── sewing-floor operation breakdown
    ↓
Production (ERPNext Work Order / BOM)
```

This is the **pre-order layer** ERPNext lacks. Everything downstream of the
sales order is already ERPNext's job.

### 1.3 Users

| Persona | Needs |
|---|---|
| **Merchandiser** | Build the style, enter consumption and rates, send the quote |
| **Costing manager** | Defend the margin, compare costing versions, approve before quoting |
| **Production planner** | SMV, operation bulletin, machine and manpower load |
| **Sourcing / purchase** | Fabric and trim requirements, nominated suppliers, lead times |
| **QA** | Lab test templates per buyer, quality instructions |

### 1.4 Why it is defensible

The costing arithmetic *is* the product. Cost cascades, SMV-driven sewing rates,
percentage cost heads on compound bases, the buyer-column mirror — this is
twenty years of garment-export practice encoded. A competitor cannot derive it
from an ERPNext BOM.

---

## 2. Current capability inventory

### 2.1 Style Master

The single core document. 110 fields, 10 tabs, submittable, amendable.

| Tab | Contents |
|---|---|
| Style Details | buyer, style name/number, merchandiser, season, segment, currency + exchange rate, size series, lead days, garment qty; `is_set` / `is_panel` / `is_pack` reveal components, panels, pack size |
| Techpack | tech pack attachments with inline preview |
| BOM | sales target, Fabric grid, Fabric Process Route, Trims grid, Trims Process Route, **costing sheet** |
| Marker | front/back design images, marker table with efficiency and width |
| SMV / Production Cost | SMV table per production category |
| Value Addition / T&A | embroidery / print / dye activities, time & action critical path |
| Logistics & Incentive Cost | incentive cost rows |
| Instructions | buyer instructions |
| Sales Price Markup | five-row markup ladder |
| Lab Test | buyer-specific lab test templates, auto-populated as materials are added |

### 2.2 The costing engine — specification

**Fabric** (47 fields) and **Trims** (49 fields). Every quantity and cost field
has a parallel *buyer* column, so company costing and buyer costing run on one row.

**Quantity cascade**

```
purchase_extra_qty   = garment_qty × purchase_extra%   / 100
production_extra_qty = garment_qty × production_extra% / 100
wastage_qty          = garment_qty × garment_wastage%  / 100

total_req_qty = ((garment_qty + purchase_extra_qty
                  + production_extra_qty + wastage_qty) × consumption)
                + sample_qty
```

Trims drive off `trims_qty` and `trims_wastage`, and add `per_garment`
(pieces of trim per garment).

**Cost cascade** — applied in this order

```
amount = rate × total_req_qty
       + insurance_amt
       + freight              (lumsum, or amount × freight% when
                               freight_based_on = Percentage)
       + import_duty%         (only when type = Import)
       + handling_charges     (only when type = Import)
       + gst%

per_piece_value = total_amt / garment_qty
```

**Manufacturing cost**

```
if based_on = SMV:
    rate = style_rate × smv ÷ efficiency        ← the core sewing formula
gst_amt = rate × gst%                           ← only when process_area = External
amount  = rate + (rate × percent_extra / 100) + gst_amt
```

**Costing sheet** — 11 auto-generated rows:

| # | Row |
|---|---|
| 1–2 | Fabric cost — local / import |
| 3–4 | Trims cost — local / import |
| 5 | Manufacturing cost |
| 6 | Other cost |
| 7 | **Total Cost (A)** |
| 8 | **Sales Price Target (B)** |
| 9 | Difference (B − A) |
| 10 | Incentive (C) |
| 11 | Difference with incentive ((B − A) + C) |

Each of rows 1–6 shows its % of Total Cost. A second currency column appears
when currency ≠ base. Total Cost (A) writes back to `cost_price_our`.

**Markup ladder** — five rows from `markup` + `increment_by`:

```
row n:  markup% = markup + (n × increment_by)
        diff    = Total Cost (A) × markup% / 100
        price   = Total Cost (A) + diff
```

### 2.3 ERPNext integration

- **51 custom fields + 16 property setters on Item** — fabric technical specs
  (GSM, construction, weave structure, warp/weft counts, finished and cuttable
  width, knitting dia, fabric segment), trim details, classification, HSN/tax,
  QR code regenerated on save.
- **Item code series** from Item Group `group_category`:
  `F-` fabric · `T-` trims · `G-` garment · `Y-` yarn · `CG-` capital goods ·
  `C-` consumables · `S-` stationery · `I-` other.
- **Item.style_master** (garment items) and **Sales Order Item.style_master**
  (read-only, fetched) — the bridge from style to order.
- **Quotation.styles** — quotes styles rather than items; standard item/tax
  layout hidden.
- `Item Group.group_category`, `Brand.is_customer_brand`, extended order types.

### 2.4 Supporting documents

**Operation Bulletin** — builds a three-rows-per-category grid (locked header /
editable lines / locked total) from the Production Category master, carrying SMV,
SSV, manpower, hourly and daily targets, machine count, rate per piece.

**Process routes** — Fabric and Trims Process Route model multi-step conversion
of an input item to a finished material: sequence, process type, input/output
item-colour-size, required qty, loss %, yarn conversion, rates.

**Masters** — ~25 master DocTypes across style, fabric/trim technical, costing,
production, lab testing and planning. Six ship with default data.

### 2.5 What exists today vs. what a product needs

| | Built | Missing |
|---|---|---|
| DocTypes | 60 | — |
| Print formats | 2 | ⏭ tech pack and Operation Bulletin, both deferred (product owner, 2026-10-06) |
| Reports | 4 | costing version comparison (deferred) |
| Dashboard charts | 3 | margin trend, cost-head contribution |
| Workflows | 1 (opt-in) | — |
| Notifications | 2 (approval) | T&A milestones — the T&A rows hold days, not dates |
| Roles | 3 + System Manager | Buyer (read-only) |
| Settings single | ✅ Style Costing Settings | base currency, precision |
| Migration patches | 2 | one per schema change from here on |
| Server-side costing API | **none** | all computation is client-side |
| CI | workflow added | not yet seen to pass |
| Licence file | ✅ GPL-3.0 | — |

---

## 3. Gaps that block generic use

These are **not** cosmetic. Each one is something a second customer hits on day one.

### 3.1 Hardcoded to the originating client

| Gap | Required |
|---|---|
| ~~Naming series is `CMV-STYLE-.YYYY.-` — the original client's initials~~ | ✅ **Resolved** — default is `STY-.YYYY.-.####`, changeable in Style Costing Settings |
| ~~Seven fixture DocTypes ship that client's master data (their merchandiser names, their cost heads)~~ | ✅ **Resolved** — six generic masters ship as fixtures; merchandisers moved to `demo/` with placeholder names. Installing the demo set in one action is Phase 4. |
| ~~Repo name does not match app name~~ | ✅ **Resolved** — app, module and repo are all `style_costing` / Style Costing. `bench get-app <url>` now resolves without an explicit name argument. |

### 3.2 The costing model is too narrow for real cost sheets

| Gap | Evidence from production cost sheets | Required |
|---|---|---|
| **`Other Cost.charge_on` offers only `Gar Qty` and `Sale Price`** | Real sheets charge percentage cost heads on **Total RM Cost**, **Total RM + Manufacturing Cost** and **Cumulative Total** — e.g. sourcing at 2% of RM, seconds allowance at 2% of RM + manufacturing, insurance at 0.25% of the running cumulative total | Extend `charge_on` to all five bases and implement each in the calculation |
| **`fabric_type` / `trims_type` are a closed list** (Local / Process / Stock / Import / Buyer) | Factories use their own source taxonomy — purchase-local, purchase-import, nominated, buyer-supplied, in-house | Make source a master DocType, not a Select, with a flag marking which values count as "import" for the costing-sheet split |
| **No pack ratio** | Carton lines read `Cons 1.00 × Rate 4.30 = Amount 0.301` — the rate is per carton and the carton holds ~15 garments. The row cannot be expressed | Add `pack_qty` / `units_per_pack` to Fabric and Trims; divide through in the cost cascade |
| **One costing per style** | Buyers negotiate. Quote v1, v2, v3 against the same style is normal | Costing versions with a comparison view |
| **Costing is per-garment only** (`garment_qty`) | Real quotes price 3,000 pieces differently from 10,000 | Quantity-break table; rates and amortised costs per break |
| **No `company` field on Style Master** | Any group with more than one legal entity | Add `company`, default it, and filter masters by it |
| **Floating-point precision fixed at site level** | Cost sheets quote line amounts to 3 decimals; a 2-decimal site rounds 0.095 → 0.10 and the sections stop tying out | Set field-level precision on amount fields in the DocType, not at site level |

### 3.3 Onboarding cannot be completed unaided

| Gap | Impact |
|---|---|
| **`group_category` must be hand-set on every Item Group** before any material appears in the Fabric/Trims pickers | A new customer with an existing item catalogue sees empty pickers and no explanation. This is the single most likely cause of a failed trial. |
| No setup wizard, no onboarding checklist | Every install needs the vendor present |
| No sample/demo dataset that can be installed and removed cleanly | Nothing to show in a trial without polluting the customer's data |

### 3.4 Conflicts with other apps

`override_doctype_class` claims **Item**. Any other apparel or manufacturing app
that also overrides Item wins or loses the MRO silently — and when this app
loses, the `F-`/`T-` naming series and QR generation **stop running with no
error**. Item creation then fails with a bare "Item Code is required".

**Required:** detect the collision at install and migrate time, warn explicitly,
and provide a setting to disable this app's Item naming so it can coexist.

### 3.5 Reconciliation between costing and manufacturing

The costing sheet and the manufacturing BOM legitimately differ — a cost sheet
rolls twelve thread cones into one costing-code line; it carries different swing
tickets; it omits items that are consumed but not costed separately. Today there
is no view that shows the difference, so nobody can answer *"is my BOM consistent
with what I quoted?"*

**Required:** a reconciliation report — materials in the BOM but not the costing,
in the costing but not the BOM, and quantity variances.

### 3.6 No BOM generation

A style knows its materials, its colours and its size range. Producing an
ERPNext BOM per variant is mechanical, and today it is manual — a style with
five colours and seven sizes needs 35 BOMs built by hand.

**Required:** one action on Style Master that generates or refreshes an ERPNext
BOM for every variant of the linked item template.

---

## 4. The architectural decision to make first

### 4.1 Move costing to the server

All eleven costing-sheet rows, the markup ladder and every row total are computed
in `style_form.js` (2,591 lines) and only land in fields on save.

**Consequences today:**

- no API — a style cannot be costed programmatically, in bulk, or from an integration
- no recompute — changing a cost head or rate master re-costs nothing
- no reporting on intermediate values
- **data created by import, API or script silently skips the arithmetic** and
  saves with zero or stale costs
- the form marks itself dirty on load, because the script writes during render

**Target:** a server method `calculate_costing(style) → dict`, called by the
client and by `validate`, with the client rendering the returned figures rather
than computing them.

**This single change unlocks** reports, bulk re-costing, costing versions, the
public API, data import, and most of §4.2. It is the difference between a form
and a product.

### 4.2 What server-side costing then enables

| Reports | Dashboard | Automation |
|---|---|---|
| Style Costing Summary | Styles by buyer / season | Costing approval workflow |
| Style-wise Margin Analysis | Average margin % trend | T&A milestone alerts |
| Fabric & Trim Consumption | Cost-head contribution | Lab test due notifications |
| Buyer-wise Style Register | Styles by status | Auto-recost on rate change |
| Costing Version Comparison | Quote-to-order conversion | Scheduled re-costing |
| BOM ↔ Costing Reconciliation | | |

---

## 5. Roadmap

### Phase 0 — Make it installable *(prerequisite for everything)*

- ~~Populate the licence file; confirm the licence in `pyproject.toml` and README agree~~ ✅ done — GPL-3.0
- ~~Align repo name with app name~~ ✅ done — `style_costing` throughout
- ~~Write migration patches: the historical duplicate DocType removal, orphan
  workspace links, the app and module rename, renamed fields~~ ✅ closed —
  a clean break was chosen (§8, question 5), so pre-rename installs are not
  upgraded in place. Two patches cover what a current install needs: the
  legacy naming-series setter and the corrected fixture names. From here on,
  every schema change ships with its own patch.
- ~~De-brand the naming series; introduce **Style Costing Settings**~~ ✅ done —
  naming series, default style rate, default efficiency, default cost heads.
  Base currency comes from the Company; precision is a Phase 1 item.
- ~~Split fixtures into structural defaults and an optional demo dataset~~ ✅ done

**Done when:** a stranger can `bench get-app`, `bench install-app`, and create a
style without touching code or asking the vendor.

### Phase 1 — Make it correct

- ⏸ Extend `Other Cost.charge_on` to all five bases and implement each — *parked, §8.1*
- ⏸ Convert fabric/trim source from Select to a master with an `is_import` flag — *parked, §8.1*
- ⏸ Add pack ratio to Fabric and Trims — *parked, §8.1*
- ~~Add `company` to Style Master~~ ✅ done. The masters carry no company, so
  there is nothing to filter by it yet.
- ⏸ Set field-level precision on all amount fields — *parked, §8.1*
- ~~Detect and handle the Item override collision~~ ✅ done — warned at install
  and migrate and on the settings page; "Keep ERPNext Item Codes" turns this
  app's item naming off.

**Done when:** a production cost sheet from any garment exporter can be
reproduced exactly, out of the box, with no Customize Form changes.

### Phase 2 — Make it a product

- ~~Roles: Merchandiser, Costing Manager, Production Planner~~ ✅ done.
  Role profiles pair each with the ERPNext roles it needs.
  ⏭ **Buyer (read-only) is deferred**: Style Master shows our cost beside the
  buyer's on every row, so a read-only buyer would see our costs. It needs
  field-level permissions first.
- ~~Permission rules per role on every DocType~~ ✅ done
- ~~`track_changes` on Style Master and Operation Bulletin~~ ✅ done
- ~~Costing approval workflow (Draft → Costed → Approved → Quoted)~~ ✅ done — opt-in from the settings
- ~~Setup wizard, including the `group_category` tagging step~~ / ~~Onboarding checklist~~ ✅ done as a four-step Module Onboarding (settings, tag Item Groups, first style, summary report). The settings page also warns how many Item Groups have no category. In-app help beyond that is not written.

**Done when:** a customer can deploy, configure and operate it without the vendor.

### Phase 3 — Make it defensible

- ⏸ Server-side costing engine (§4.1) — *parked, §8.1*
- Reports and dashboard charts (§4.2) — ✅ Style Costing Summary (covers the
  buyer-wise register and margin analysis through its filters) and Fabric and
  Trim Consumption. Both read stored values only. Charts, version comparison
  and reconciliation still to do.
- ~~BOM generation from a style (§3.6)~~ ✅ done — a draft BOM per garment item linked to the style. Every variant gets the same materials; ⏭ variant-specific BOMs (size and colour rows) are deferred.
- ⏭ Costing versions with comparison — *deferred by the product owner; a snapshot inside the style is the recommended design*
- ~~BOM ↔ costing reconciliation report~~ ✅ done

**Done when:** the module does things a competitor cannot assemble from stock ERPNext.

### Phase 4 — Make it sellable

- Quantity-break pricing
- ~~Buyer-facing cost sheet print format using the existing buyer columns~~ ✅ done — line items and the sales price; no buyer total, because none is stored
- Cost sheet importer — map a customer's own spreadsheet columns onto the style
- CI running the test suite against Frappe v16 — ✅ workflow added, not yet seen to pass on GitHub
- Public documentation, changelog, semantic versioning — ✅ changelog and a user guide (`docs/user-guide.md`)
- ~~Demo dataset installable and removable in one action~~ ✅ done — masters only, no sample style

**Done when:** a prospect's own cost sheet can be imported and reproduced inside
a single demo call.

---

## 6. Risks

| Risk | Mitigation |
|---|---|
| **3,691 lines of ported client JS** carry most of the defect surface and block server-side costing | Budget a rewrite of `style_form.js` alongside Phase 3, not a patch |
| **Overlap with other apparel apps** on the ERPNext marketplace — particularly any that override Item | Decide the positioning early: either coexist (make Item naming optional) or declare a conflict |
| **Costing conventions validated against a narrow sample.** Cost-head structures, source taxonomies and efficiency models vary by factory and by country | Validate the Phase 1 model against cost sheets from at least three unrelated manufacturers before freezing the schema |
| **No production reference customer** — nobody has run a full season through it | Secure one design partner before public release; instrument for feedback |
| **Client-side-only calculation makes data import unsafe** | Phase 3 is a hard prerequisite for any import feature |

---

## 7. Success criteria

| Horizon | Criterion |
|---|---|
| Installable | Clean install on a fresh v16 bench, no vendor involvement |
| Correct | A real production cost sheet reproduces to the stated decimal precision |
| Usable | A merchandiser builds a complete style unaided in under 30 minutes |
| Operable | Deployed and configured by the customer's own admin |
| Marketable | Prospect's own cost sheet imported and reproduced in one demo |
| Supportable | Tests green in CI, documented upgrade path between versions |

---

## 8. Open questions for the product owner

1. **Positioning** — standalone apparel costing module, or one component of a
   wider apparel suite? This determines whether the Item override stays.
2. ~~**Licence** — MIT (adoption) or commercial (revenue)?~~ ✅ **Decided** —
   GPL-3.0, the same licence as ERPNext, whose `Item` class this app subclasses.
3. **Scope boundary** — does the module stop at the sales order, or extend into
   production planning and shop-floor execution?
4. **Multi-currency depth** — is a single exchange rate per style enough, or is
   rate-per-material-origin required?
5. ~~**Backward compatibility** — is a clean break acceptable, or must every
   existing install upgrade in place?~~ ✅ **Decided** — clean break.
6. **Localisation** — tax handling is currently GST/HSN-shaped. How much
   abstraction is needed for non-Indian deployments?

### 8.1 Open findings in the costing code — to discuss

**Standing rule (product owner, 2026-10-06):** nothing that changes a computed
number is built until the whole module has been tested and the change is asked
for specifically. Parked on that basis: `charge_on` bases, the source master,
pack ratio, field-level precision, efficiency in the sewing rate, the
server-side costing engine, quantity-break pricing and the cost sheet importer.

Found while building Style Costing Settings. Neither is changed yet; both
belong to Phase 1.

1. **Efficiency is never used.** §2.2 gives the sewing rate as
   `style_rate × smv ÷ efficiency`, but `set_final_mf_rate` in `style_form.js`
   computes `rate × smv` only. The SMV row's `efficiency_cost` is stored and
   ignored, so the Default Efficiency setting is a prefill with no effect on
   cost yet.
2. **Percentage cost heads only work for one name.** A percentage in Other Cost
   is applied only when the cost head is literally named `COMMISSION`, and
   always on the sales price target (`update_rate_our_oc`). Any other head with
   "Percentage" selected calculates nothing.
