# Step-by-Step: Migrating Policies from VMware NSX to Cisco Secure Workload

A hands-on runbook for moving DFW policy from **VMware NSX-T** to **Cisco Secure Workload (CSW)**. Follow it top to bottom, **per application/scope**. For the concepts behind each step, see the [main guide](../CSW-NSX-Migration-Guide.md); for field-by-field object translation, keep the [mapping cheat sheet](NSX-to-CSW-MAPPING-CHEATSHEET.md) open.

> **Golden rule (repeat after me):** never enforce the same application on NSX **and** CSW at the same time. Cut over one app at a time; rollback = disable CSW enforcement on that scope.

---

## Prerequisites

- [ ] CSW reachable (SaaS URL or on-prem cluster) with an admin/site-admin login
- [ ] CSW **agents installed** on in-scope workloads, **enforcement OFF** (deep-visibility)
- [ ] **vCenter integration** configured in CSW (so VM tags/attributes arrive as labels)
- [ ] NSX **read-only** service account + reachability to NSX Manager
- [ ] `python3` + `requests` for the export helper
- [ ] Decide the **first app** to migrate (pick a low-risk, well-understood one)

---

## Part 1 — Export the NSX policy (baseline)

**Step 1.1 — Export Groups, DFW rules, and Services to CSV.**

```bash
cd scripts
pip install requests
export NSX_MANAGER="nsxmgr.example.com"
export NSX_USER="svc-nsx-ro"
export NSX_PASSWORD="..."          # or omit to be prompted
python3 nsx_export.py --out-dir ./nsx-export
```

Produces:
- `nsx_groups.csv` — group id, name, membership criteria (+ CSW label/filter hints)
- `nsx_dfw_rules.csv` — policy, category, rule, src/dst groups, services, L7 profiles, action, applied-to (+ CSW priority hint)
- `nsx_services.csv` — service id, name, protocol, ports

**Step 1.2 — Scope the CSV to your first app.** Filter `nsx_dfw_rules.csv` to the Security Policy / Groups for the app you're migrating first. This is your **source-of-truth rule list** for that app.

**Step 1.3 — Note the "intent gaps."** Flag any rules using **Context Profiles (L7 App-ID)**, **Distributed IDS/IPS**, or **Identity Firewall** — these need the substitutes in [§4 of the main guide](../CSW-NSX-Migration-Guide.md#4-capability-deltas-you-must-plan-for) (process/FQDN policy, Secure Firewall, ISE).

---

## Part 2 — Build the CSW label & scope foundation

**Step 2.1 — Confirm labels are populated.** In CSW: **Organize → Inventory** (or *Inventory Search*). Search a known workload and confirm it carries the vCenter-derived labels (name, OS, tags). If NSX tags aren't present as labels yet, add them via the vCenter connector or upload a CSV (**Organize → Labels → Upload**).

**Step 2.2 — Create the scope for the app.** **Organize → Scopes and Inventory → Create Scope**. Build a query that matches the app's workloads (e.g. `orchestrator_system/vcenter_tag = app=payments`). Nest it under the right parent (e.g. `Default → Prod → Payments`).

**Step 2.3 — Recreate NSX Groups as inventory filters.** For each NSX Group used by the app's rules, create a matching **Inventory Filter** (**Organize → Inventory Filters → Create**) using the same criteria from `nsx_groups.csv`. Prefer **label-based (dynamic)** queries over static IP lists so new VMs inherit policy.

> Tip: name filters after the NSX Group so the mapping is obvious during review.

**Step 2.4 — Validate membership.** Open each filter and confirm the member workloads match what NSX shows for that Group. Reconcile discrepancies now (missing agents, label drift).

---

## Part 3 — Translate rules into a CSW workspace

**Step 3.1 — Create a workspace for the app.** **Defend → Segmentation → (select the scope) → Create Workspace**. One workspace per app/scope.

**Step 3.2 — Enter translated policies.** For each row in your scoped `nsx_dfw_rules.csv`, add a CSW policy:

| NSX rule field | CSW policy field |
|---|---|
| Source Group | **Consumer** (inventory filter) |
| Destination Group | **Provider** (inventory filter) |
| Service (port/proto) | **Protocols and Ports** |
| Action (Allow/Drop) | **Allow / Deny** |
| Category (Infra/Env/App) | Priority band → **Absolute / Default / Catch-all** |

Map NSX categories to CSW priority: **Emergency/Infrastructure → Absolute**, **Environment/Application → Default**, last-resort → **Catch-all**.

**Step 3.3 — Set a safe catch-all.** Keep the workspace's default posture **permissive-with-logging** for now (do **not** set default-deny yet). You'll tighten after analysis.

**Step 3.4 — Handle the gap rules.** For flagged L7/IDS/Identity rules, encode the closest CSW equivalent (process-based or FQDN-based policy) and note the ones that will be handled by Secure Firewall / ISE instead.

---

## Part 4 — Discover what you missed (ADM) and prove it (analysis)

**Step 4.1 — Run ADM to catch implicit flows.** In the workspace, **Automatic Policy Discovery → Run ADM** over a window that covers a full business cycle. ADM proposes policies from *actual* flows — this surfaces traffic NSX allowed via broad/any-any rules that your literal translation would miss.

**Step 4.2 — Merge ADM output with your translated rules.** Approve ADM suggestions that represent real intent; keep your explicit NSX-derived rules where they're stricter. Resolve conflicts in favor of least privilege.

**Step 4.3 — Turn on Live Policy Analysis.** Enable **Analysis** on the workspace. CSW now compares your draft policy against live flows **without enforcing**.

**Step 4.4 — Drive escaped flows to zero.** In **Analysis → Rejected/Escaped flows**, review anything that *would* be dropped:
- Legitimate but missing → add/adjust a policy.
- Unexpected → investigate (possible over-permissive NSX rule you should *not* carry forward).

Iterate until analysis is clean for the full window. **This is the safety gate before enforcement.**

---

## Part 5 — Cut over (per application)

> Do this in a change window. NSX is still enforcing the app until Step 5.2.

**Step 5.1 — Enable CSW enforcement on the workspace.** **Enforce → Enable Enforcement** (agents now program the host firewall for this scope). Confirm agents show enforcement **Enabled** (**Manage → Agents**).

**Step 5.2 — Remove the matching NSX DFW rules.** In NSX Manager, disable/delete exactly the rules for this app (from your scoped CSV). This prevents double-enforcement.

**Step 5.3 — Validate.**
- App health / smoke tests pass.
- Expected allows work; expected denies are blocked.
- CSW **Enforcement → Concrete Policies** on a sample workload shows the rules you expect.
- No unexpected drops in flow view.

**Step 5.4 — Rollback (if needed).** Disable enforcement on the CSW workspace. If you haven't yet deleted the NSX rules, NSX resumes; otherwise your permissive-with-logging baseline keeps the app up while you fix policy.

**Step 5.5 — Tighten the catch-all.** Once stable, move the workspace default from permissive-with-logging to **default-deny** for true zero-trust.

---

## Part 6 — Repeat, then decommission

**Step 6.1 — Repeat Parts 1–5** for the next app, expanding from low-risk to tiered/critical apps.

**Step 6.2 — Retire NSX DFW.** When *all* apps are enforced on CSW and stable, remove the remaining NSX DFW rule base.

**Step 6.3 — Reclaim licensing.** Reclaim NSX licensing per your VMware/Broadcom agreement. Keep NSX only for anything intentionally out of CSW scope (e.g. N-S Gateway Firewall) or replace with the appropriate Cisco product.

**Step 6.4 — Operationalize.** Run the ongoing lifecycle in CSW: ADM → analysis → enforce for changes, plus forensics and compliance reporting.

---

## Per-app cutover checklist (copy for each application)

- [ ] NSX rules for the app exported and scoped (`nsx_dfw_rules.csv`)
- [ ] Scope created; NSX Groups recreated as inventory filters; membership validated
- [ ] Workspace created; rules translated; catch-all = permissive-with-logging
- [ ] ADM run and merged; gap rules addressed (L7 / IDS / Identity)
- [ ] Live analysis clean for a full business cycle (zero unexpected drops)
- [ ] Change window scheduled; rollback plan confirmed
- [ ] CSW enforcement enabled → matching NSX rules removed
- [ ] Post-cutover validation passed
- [ ] Catch-all tightened to default-deny
- [ ] App marked migrated

---

*UI paths reflect recent CSW releases and may differ slightly by version; confirm against the [official documentation](00-official-references.md) for your release.*
