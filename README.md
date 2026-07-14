# Migrating from VMware NSX to Cisco Secure Workload (CSW)

![Visitors](https://visitor-badge.laobi.icu/badge?page_id=chandrapati.csw-nsx-migration&left_text=visitors)
[![GitHub stars](https://img.shields.io/github/stars/chandrapati/csw-nsx-migration?style=social)](https://github.com/chandrapati/csw-nsx-migration/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/chandrapati/csw-nsx-migration)](https://github.com/chandrapati/csw-nsx-migration/commits/main)

A practitioner's guide for moving **east-west microsegmentation** from **VMware NSX-T Distributed Firewall (DFW)** to **Cisco Secure Workload** — the architectural shift, a full **object-model mapping**, the **capability deltas** to plan for, and a **phased, risk-managed cutover** that keeps you protected the entire way.

[![Cisco Secure Workload](https://img.shields.io/badge/Cisco-Secure%20Workload-00205B?logo=cisco&logoColor=white)](https://www.cisco.com/go/secureworkload)
[![From](https://img.shields.io/badge/From-VMware%20NSX--T%20DFW-5A6A72?logo=vmware&logoColor=white)](https://techdocs.broadcom.com/us/en/vmware-cis/nsx.html)
[![Play](https://img.shields.io/badge/Play-Microsegmentation%20Migration-0AA34F)](https://www.cisco.com/site/us/en/products/security/secure-workload/index.html)

> **⚠ Disclaimer:** Community field guide from Cisco Solutions Engineering, summarized from **public Cisco & VMware documentation** — **not** an official product document and not a competitive teardown. Verify against the [official guides](CSW-NSX-Migration-Guide.md#14-official-references). Trademarks belong to their respective owners.

---

## The shift in one line

**Enforcement moves from the ESXi hypervisor kernel (VMware-only) to the workload OS (any platform).** That's what makes CSW portable across bare metal, VMs, containers, and cloud — and it's the thing you plan the migration around (an agent goes on each workload).

---

## Diagrams

| | |
|---|---|
| **Enforcement model: NSX vs CSW** | ![compare](nsx-vs-csw-architecture.png) |
| **Object-model mapping (with gaps)** | ![mapping](nsx-to-csw-object-mapping.png) |
| **Phased migration + coexistence** | ![phases](nsx-to-csw-migration-phases.png) |

---

## Object mapping (quick view)

| VMware NSX | Cisco Secure Workload |
|---|---|
| NSX Tag / VM attribute | Label / annotation |
| Group (dynamic/static) | Inventory filter / Scope |
| Security Policy + Category | Workspace + policy priority |
| DFW rule (src/dst/svc/action) | Policy (consumer→provider) |
| Services | Protocols & ports |
| Applied To | Scope assignment |
| Context Profile (L7 App-ID) | Process + L4 context ⚠ |
| Distributed IDS/IPS | Forensics + Secure Firewall ⚠ |
| Identity Firewall | Cisco ISE integration ⚠ |

⚠ = capability delta — see the [guide §4](CSW-NSX-Migration-Guide.md#4-capability-deltas-you-must-plan-for).

---

## The 7 phases

1. **Discover** — agents in deep-visibility, import vCenter tags → labels
2. **Model** — scope tree + inventory filters mirror NSX Groups
3. **Translate** — DFW rules → CSW policies, accelerated by **ADM**
4. **Analyze** — live policy analysis vs observed flows (no enforce)
5. **Parallel run** — NSX enforces, CSW observes (coexistence)
6. **Cutover** — per app: enable CSW enforce, remove matching NSX rules
7. **Decommission** — retire NSX DFW, reclaim licensing

**Golden rule:** never enforce the same app on NSX and CSW at once — cut over **per application**.

---

## Repository contents

| Path | Description |
|---|---|
| [`CSW-NSX-Migration-Guide.md`](CSW-NSX-Migration-Guide.md) | The full guide (14 sections, 3 diagrams) |
| [`nsx-vs-csw-architecture.png`](nsx-vs-csw-architecture.png) | Enforcement-model comparison |
| [`nsx-to-csw-object-mapping.png`](nsx-to-csw-object-mapping.png) | Object mapping + capability gaps |
| [`nsx-to-csw-migration-phases.png`](nsx-to-csw-migration-phases.png) | Phased timeline + coexistence lanes |
| [`make_architecture.py`](make_architecture.py) | Regenerates all three diagrams (matplotlib) |
| [`docs/NSX-to-CSW-MAPPING-CHEATSHEET.md`](docs/NSX-to-CSW-MAPPING-CHEATSHEET.md) | One-page mapping cheat sheet |
| [`docs/MIGRATION-PLANNING-CHECKLIST.md`](docs/MIGRATION-PLANNING-CHECKLIST.md) | Printable planning checklist |
| [`docs/00-official-references.md`](docs/00-official-references.md) | Official Cisco + VMware links |
| [`build.sh`](build.sh) | Builds HTML/PDF from the Markdown |

---

## Build the HTML/PDF

```bash
./build.sh
```

Requires `pandoc` and Google Chrome (for PDF). Regenerate diagrams with `python3 make_architecture.py` (needs `matplotlib`).

---

## Related guides

Part of the **[CSW User-Education](https://github.com/chandrapati/CSW-User-Education)** series:

- [CSW vCenter Integration](https://github.com/chandrapati/csw-vcenter-integration) — get NSX tags into CSW as labels
- [CSW Policy Lifecycle](https://github.com/chandrapati/CSW-Policy-Lifecycle) — ADM, analysis, enforcement
- [CSW Agent Installation](https://github.com/chandrapati/CSW-Agent-Installation-Guide)
- [CSW Virtual (CSW-V) vSphere Deployment](https://github.com/chandrapati/csw-virtual-vsphere-deployment)

---

*Maintained by Cisco Solutions Engineering. Summarized from public Cisco & VMware documentation; example values only. Not an official product document.*
