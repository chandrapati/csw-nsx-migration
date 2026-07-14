# NSX → CSW migration planning checklist

Hand this to the customer's **VMware/NSX**, **security**, **networking**, and **application** teams. Work top-to-bottom; do not enable CSW enforcement until Phase 4 is clean.

## A. Scope & discovery (Phase 1)

- [ ] In-scope estate defined (which apps / clusters / environments migrate, and in what order)
- [ ] Inventory of NSX **Groups**, **Security Policies**, **Services**, **Context Profiles** exported (for reference)
- [ ] Distributed IDS/IPS and Identity Firewall usage inventoried (delta planning)
- [ ] CSW deployment chosen: **SaaS** or **on-prem** (39RU/8RU)
- [ ] CSW **agents installed** (deep-visibility, enforcement OFF) on in-scope Linux/Windows workloads
- [ ] Cloud/other workloads covered (agentless connector where applicable)
- [ ] **vCenter integration** live → VM tags/attributes flowing in as labels
- [ ] Flow + process telemetry collected across a representative business cycle

## B. Labeling & scopes (Phase 2)

- [ ] Label taxonomy / naming convention agreed
- [ ] Source of truth for labels (vCenter / CMDB / ServiceNow) identified
- [ ] NSX **Tags** reproduced as CSW **labels**
- [ ] NSX **Groups** reproduced as CSW **inventory filters** (dynamic where possible)
- [ ] **Scope tree** designed to mirror NSX domains/tiers (e.g. Env → App → Tier)
- [ ] Scope membership validated against NSX group membership

## C. Policy translation (Phase 3)

- [ ] **ADM** run per scope; discovered policy reviewed
- [ ] NSX DFW rule intent reconciled against ADM output (explicit vs implicit/any-any)
- [ ] Rules translated: source/dest Groups → consumer/provider filters; Services → ports/proto; action → allow/deny
- [ ] Category/order mapped to Absolute / Default / Catch-all priority
- [ ] Permissive-with-logging baseline in place (no premature default-deny)
- [ ] Deltas addressed: L7 App-ID → process/FQDN + Secure Firewall; IDS/IPS → Secure Firewall; Identity FW → ISE

## D. Analysis (Phase 4)

- [ ] **Live policy analysis** enabled (no enforcement)
- [ ] Escaped/dropped flows reviewed and resolved
- [ ] Over-permissive rules tightened
- [ ] Analysis clean across a full business cycle for each app

## E. Coexistence & cutover (Phases 5–6)

- [ ] Parallel run validated (NSX enforcing, CSW monitoring)
- [ ] Operational runbooks ready (change mgmt, exceptions, alerting, on-call)
- [ ] First cutover = **low-risk app**; window + rollback plan approved
- [ ] Per app: **enable CSW enforcement** → **remove matching NSX DFW rules** → validate
- [ ] Confirmed: no app enforced by NSX **and** CSW simultaneously
- [ ] App health + expected allows/denies verified post-cutover

## F. Decommission (Phase 7)

- [ ] All in-scope apps enforced by CSW and stable
- [ ] NSX DFW rule base retired
- [ ] NSX licensing reclaimed per Broadcom/VMware agreement
- [ ] Residual NSX use (N-S gateway / overlay) documented or replaced
- [ ] Segmentation lifecycle operating in CSW (ADM → analysis → enforce)

## G. Rollback (any time before decommission)

- [ ] Rollback = disable CSW enforcement on the affected scope
- [ ] NSX (or permissive baseline) resumes control
- [ ] Incident/rollback path tested at least once
