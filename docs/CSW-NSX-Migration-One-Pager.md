# From VMware NSX to Cisco Secure Workload — Customer One-Pager

*Hypervisor-independent microsegmentation: one policy model for every workload — bare metal, VM, container, and cloud.*

## Why move now
- **Licensing & cost** — re-evaluate spend after the Broadcom/VMware packaging changes.
- **No platform lock-in** — NSX enforces in the ESXi kernel (VMware only); CSW enforces in the workload OS (any platform).
- **Multicloud, one model** — consistent segmentation across on-prem, AWS, Azure, GCP, and Kubernetes.
- **Discovery, not guesswork** — CSW's ADM auto-discovers policy from real flow + process telemetry.

## The shift
**Enforcement moves from the hypervisor kernel → the workload OS.** A lightweight CSW agent (Linux iptables/ipset, Windows WFP) enforces per host; cloud can be agentless.

## What maps cleanly
| VMware NSX | Cisco Secure Workload |
|---|---|
| Tags / VM attributes | Labels (from vCenter, CMDB, ServiceNow) |
| Groups (dynamic/static) | Inventory filters + Scopes |
| Security Policy / Category | Workspace + policy priority |
| DFW rules (src/dst/svc/action) | Policies (consumer→provider) |

## Plan for these deltas
- **L7 App-ID (DPI)** → process + FQDN policy, with Cisco Secure Firewall / Hypershield for true L7.
- **Distributed IDS/IPS** → Cisco Secure Firewall (CSW adds forensics, behavior, vulnerability context).
- **Identity Firewall (AD user)** → Cisco ISE user/device context.

## How we de-risk the migration (7 phases)
**Discover → Model → Translate (ADM) → Analyze → Parallel run → Cutover (per app) → Decommission.**
NSX keeps enforcing until each app's CSW policy is proven in live analysis. We cut over **one application at a time**, then retire the matching NSX rules. Rollback is always "disable CSW enforcement on that scope."

**Golden rule:** never enforce the same app on NSX and CSW at once.

## Outcome
Portable, zero-trust microsegmentation across your entire estate — with lower platform dependency and richer visibility — delivered through a controlled, reversible, per-application cutover.

> *Cisco Solutions Engineering. Summarized from public Cisco & VMware documentation; not an official product document. Trademarks belong to their respective owners.*
