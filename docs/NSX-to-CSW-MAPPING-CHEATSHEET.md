# NSX → CSW mapping cheat sheet

One-page reference for translating VMware NSX-T constructs to Cisco Secure Workload. Keep it next to the NSX Manager and the CSW workspace while you translate.

## Grouping & identity

| NSX-T | CSW | Translation tip |
|---|---|---|
| NSX **Tag** (`scope|tag`) | **Label** key/value | Ingest via vCenter connector; or CMDB/CSV. Keep NSX tag semantics as label keys |
| VM **name / OS / segment** criteria | Label from vCenter attributes | Map each NSX criterion to a label dimension |
| **Group** (dynamic criteria) | **Inventory filter** (query) | `tag = X AND env = Prod` → same query in the filter builder |
| **Group** (static members) | Filter by explicit label or IP set | Prefer dynamic; use static only for appliances |
| Nested Groups | Filters referencing filters / scope hierarchy | Flatten into the scope tree where possible |

## Policy structure

| NSX-T | CSW | Translation tip |
|---|---|---|
| **Domain** | Top-level **Scope** | e.g. `Default`, per-BU |
| **Security Policy** | **Workspace** (per scope) | One workspace per app/scope |
| **Category** (Ethernet→Emergency→Infra→Env→App) | **Policy priority** (Absolute → Default → Catch-all) | Emergency/Infra → Absolute; App → Default; last-resort → Catch-all |
| Rule order within policy | Order within priority band | Preserve intent, not literal order |

## Rule fields

| NSX-T rule field | CSW policy field | Notes |
|---|---|---|
| **Source Group** | **Consumer** filter | Direction = consumer→provider |
| **Destination Group** | **Provider** filter | |
| **Service** (port/proto) | **Protocols & ports** | Near 1:1 (TCP/UDP/ICMP...) |
| **Action** (Allow/Drop/Reject) | **Allow / Deny** | |
| **Applied To** | **Scope** binding | Where the policy is enforced |
| **Logging** | Policy logging / flow visibility | Keep logging during migration |
| **Stateful** | Stateful (default) | Both stateful |

## Capability deltas (plan around these)

| NSX-T | CSW substitute |
|---|---|
| **Context Profile / L7 App-ID (DPI)** | Process-based policy + FQDN policy; true L7 at Secure Firewall/Hypershield |
| **Distributed IDS/IPS** | CSW forensics/behavior/vuln + Cisco Secure Firewall for IDS/IPS |
| **Identity Firewall (AD user)** | Cisco ISE user/device context |
| **Gateway Firewall (N-S)** | Out of CSW scope — use NGFW |

## Enforcement mechanics

| | NSX-T | CSW |
|---|---|---|
| Where | ESXi kernel @ vNIC | Guest OS host firewall |
| Linux | n/a (kernel) | `iptables` / `ipset` |
| Windows | n/a (kernel) | **WFP** (or WAF mode) |
| Prereq | ESXi transport node | **Agent installed** on each workload |

> **No automated importer** exists — translate deliberately, but let **ADM** propose policy from real flows so you're validating intent, not hand-copying rules.
