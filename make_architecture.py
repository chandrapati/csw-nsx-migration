#!/usr/bin/env python3
"""Diagrams for the VMware NSX -> Cisco Secure Workload (CSW) migration guide.

Generates three PNGs:
  1) nsx-vs-csw-architecture.png    - enforcement-model comparison: NSX kernel DFW
                                      vs CSW host-agent / connector microsegmentation.
  2) nsx-to-csw-object-mapping.png  - object-model mapping (Groups->filters, Security
                                      Policy->workspace, DFW rule->policy, tags->labels)
                                      plus the honest capability gaps.
  3) nsx-to-csw-migration-phases.png- phased migration timeline with the NSX/CSW
                                      coexistence (parallel-run) lane and per-app cutover.

Run:  python3 make_architecture.py
Requires: matplotlib
"""
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# ---- palette ----------------------------------------------------------------
NAVY = "#00205B"
BLUE = "#007BC7"
CYAN = "#00BCEB"
GRN = "#0AA34F"
AMBER = "#B5772C"
PURP = "#7B4FA0"
RED = "#C0392B"
INK = "#1A1A2E"
GREY = "#555555"
LIGHT = "#F5F8FC"
BLUEBG = "#EAF4FB"
GRNBG = "#E8F6EE"
AMBBG = "#F7EFE4"
PURPBG = "#F1EAF7"
REDBG = "#FBEBE9"
# VMware-ish
VMW = "#5A6A72"
VMWBG = "#EDEFF1"
VMGRN = "#6DA544"
VMGRNBG = "#EDF4E8"


def _box(ax, x, y, w, h, edge, fc="white", lw=1.4, rounding=0.7, z=2, ls="solid"):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0,rounding_size={rounding}",
                 linewidth=lw, edgecolor=edge, facecolor=fc, zorder=z, linestyle=ls))


def _txt(ax, x, y, s, size=11, color=INK, weight="normal", ha="center", va="center", z=5, rot=0):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va,
            zorder=z, rotation=rot, fontfamily=["Helvetica Neue", "Arial", "DejaVu Sans"])


def _arrow(ax, p0, p1, color, lw=2.0, style="-|>", ls="solid", z=6, ms=16):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms,
                 lw=lw, color=color, zorder=z, linestyle=ls))


def _wordmark(ax, lx, ly):
    for i, hh in enumerate([1.4, 2.3, 3.2, 2.3, 1.4, 2.3, 3.2, 4.1, 3.2, 2.3, 1.4]):
        ax.add_patch(Rectangle((lx + i * 0.62, ly - hh / 2), 0.26, hh,
                     facecolor=NAVY, edgecolor="none", zorder=6))
    _txt(ax, lx + 11 * 0.31, ly - 3.0, "CISCO", size=8, color=NAVY, weight="bold")


def _gradient_bar(ax, x0, y0, width, height):
    for i in range(200):
        frac = i / 199
        if frac < 0.6:
            t = frac / 0.6; r = 0x00; g = int(0x20 + t * (0x7b - 0x20)); b = int(0x5b + t * (0xc7 - 0x5b))
        else:
            t = (frac - 0.6) / 0.4; r = 0x00; g = int(0x7b + t * (0xbc - 0x7b)); b = int(0xc7 + t * (0xeb - 0xc7))
        ax.add_patch(Rectangle((x0 + frac * width, y0), width / 200 + 0.2, height,
                     facecolor=f"#{r:02x}{g:02x}{b:02x}", edgecolor="none", zorder=2))


# =============================================================================
# Diagram 1 - NSX vs CSW enforcement model
# =============================================================================
def diagram_compare():
    fig, ax = plt.subplots(figsize=(14.4, 8.8), dpi=100)
    ax.set_xlim(0, 144); ax.set_ylim(0, 88); ax.axis("off")

    _txt(ax, 60, 84.6, "Enforcement Model \u2014 VMware NSX Distributed Firewall  vs  Cisco Secure Workload",
         size=15.0, color=NAVY, weight="bold")
    _wordmark(ax, 129, 83.2)

    # ---------------- LEFT: NSX ---------------------------------------------
    _box(ax, 3, 16, 66, 63, VMW, VMWBG, lw=2.2, rounding=1.2, z=1)
    _txt(ax, 36, 76.4, "VMware NSX-T \u2014 Distributed Firewall (DFW)", size=11.2, color=VMW, weight="bold")
    _txt(ax, 36, 73.8, "enforcement inside the ESXi hypervisor kernel", size=7.6, color=GREY)

    _box(ax, 22, 66.5, 28, 5.6, VMGRN, VMGRNBG, lw=1.6)
    _txt(ax, 36, 69.3, "NSX Manager cluster", size=8.6, color=VMGRN, weight="bold")
    _txt(ax, 36, 67.6, "authors Groups \u00b7 Security Policies", size=6.6, color=GREY)

    # two ESXi hosts w/ kernel DFW + VMs
    for hx in (7, 38):
        _box(ax, hx, 30, 25, 30, VMW, "white", lw=1.6, rounding=0.8)
        _txt(ax, hx + 12.5, 57.2, "ESXi host", size=8.4, color=VMW, weight="bold")
        _box(ax, hx + 2, 49.5, 21, 5.2, RED, REDBG, lw=1.4)
        _txt(ax, hx + 12.5, 52.1, "kernel DFW module", size=7.4, color=RED, weight="bold")
        for i in range(3):
            vx = hx + 2 + i * 7.0
            _box(ax, vx, 33, 6.2, 12.5, BLUE, BLUEBG, lw=1.1, rounding=0.4)
            _txt(ax, vx + 3.1, 43.5, "VM", size=6.8, color=BLUE, weight="bold")
            _box(ax, vx + 0.7, 34.2, 4.8, 2.2, VMGRN, "white", lw=0.8, rounding=0.2)
            _txt(ax, vx + 3.1, 35.3, "vNIC", size=5.2, color=VMGRN, weight="bold")
        _arrow(ax, (36, 66.5), (hx + 12.5, 55), VMGRN, lw=1.4, ls="dashed", z=4, ms=11)

    _box(ax, 7, 18, 56, 9.5, VMW, "white", lw=1.4, rounding=0.6)
    _txt(ax, 35, 25.2, "Scope: VMware vSphere estate only", size=8.2, color=VMW, weight="bold")
    for i, ln in enumerate([
        "\u2022 Rules follow the VM; enforced at the vNIC, in-kernel",
        "\u2022 Objects: Groups \u00b7 Security Policy/Category \u00b7 Services \u00b7 Context Profile (L7 App-ID)",
        "\u2022 Also: Distributed IDS/IPS \u00b7 Identity Firewall \u00b7 Gateway FW (N-S)",
    ]):
        _txt(ax, 9, 23.2 - i * 2.0, ln, size=6.7, color=INK, ha="left")

    # ---------------- RIGHT: CSW --------------------------------------------
    _box(ax, 75, 16, 66, 63, BLUE, BLUEBG, lw=2.2, rounding=1.2, z=1)
    _txt(ax, 108, 76.4, "Cisco Secure Workload \u2014 host-based microsegmentation", size=10.6, color=NAVY, weight="bold")
    _txt(ax, 108, 73.8, "enforcement inside each OS \u00b7 any workload, any location", size=7.6, color=GREY)

    _box(ax, 92, 66.5, 32, 5.6, NAVY, "white", lw=1.6)
    _txt(ax, 108, 69.3, "CSW cluster (39RU/8RU) or SaaS", size=8.2, color=NAVY, weight="bold")
    _txt(ax, 108, 67.6, "labels \u00b7 scopes \u00b7 workspaces \u00b7 ADM", size=6.6, color=GREY)

    # heterogeneous workloads with agents
    wls = [
        (79, "VM\n(vSphere)", BLUE),
        (89.4, "Bare\nmetal", AMBER),
        (99.8, "K8s\npod", PURP),
        (110.2, "AWS/\nAzure/GCP", GRN),
        (120.6, "Windows\nserver", CYAN),
    ]
    for wx, lbl, col in wls:
        _box(ax, wx, 38, 9.4, 16, col, "white", lw=1.3, rounding=0.5)
        _txt(ax, wx + 4.7, 50.6, lbl, size=6.4, color=col, weight="bold")
        _box(ax, wx + 0.9, 39.4, 7.6, 4.4, GRN, GRNBG, lw=1.1, rounding=0.3)
        _txt(ax, wx + 4.7, 41.6, "agent", size=5.8, color=GRN, weight="bold")
        # policy push down + telemetry up
        _arrow(ax, (108, 66.5), (wx + 4.7, 54), NAVY, lw=1.0, ls="dashed", z=4, ms=9)

    _txt(ax, 108, 35.4, "policy push \u2193      \u2191 flow + process telemetry (fuels ADM)", size=6.8, color=GREY, weight="bold")

    _box(ax, 79, 18, 58, 15.5, BLUE, "white", lw=1.4, rounding=0.6)
    _txt(ax, 108, 31.0, "Scope: bare-metal \u00b7 VM \u00b7 container \u00b7 multicloud", size=8.2, color=NAVY, weight="bold")
    for i, ln in enumerate([
        "\u2022 Agent enforces in host firewall (Linux iptables/ipset \u00b7 Windows WFP)",
        "\u2022 Objects: Labels \u00b7 Scopes \u00b7 Inventory filters \u00b7 Workspaces \u00b7 Policies",
        "\u2022 Agentless option for cloud (AWS SG / Azure NSG / GCP FW) & ACI",
        "\u2022 ADM auto-discovers policy from real flows \u00b7 live analysis before enforce",
        "\u2022 Hypervisor-agnostic \u2014 not tied to VMware",
    ]):
        _txt(ax, 81, 29.2 - i * 2.15, ln, size=6.7, color=INK, ha="left")

    # center migration arrow
    _arrow(ax, (69, 47.5), (75, 47.5), GRN, lw=3.2, ms=22)
    _txt(ax, 72, 50.4, "migrate", size=7.6, color=GRN, weight="bold")

    _gradient_bar(ax, 3, 10.5, 138, 0.9)
    _txt(ax, 72, 7.6,
         "Key shift: enforcement moves from the hypervisor kernel (VMware-only) to the workload OS (any platform).",
         size=8.0, color=NAVY, weight="bold")
    _txt(ax, 72, 5.2,
         "Both can run at once during migration: keep NSX DFW enforcing while CSW agents observe, then cut over per application.",
         size=7.2, color=GREY)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    out = "nsx-vs-csw-architecture.png"
    plt.savefig(out, dpi=100, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", out)


# =============================================================================
# Diagram 2 - object-model mapping + gaps
# =============================================================================
def diagram_mapping():
    fig, ax = plt.subplots(figsize=(14.4, 8.8), dpi=100)
    ax.set_xlim(0, 144); ax.set_ylim(0, 88); ax.axis("off")

    _txt(ax, 60, 84.6, "Object-Model Mapping \u2014 VMware NSX  \u2192  Cisco Secure Workload",
         size=15.5, color=NAVY, weight="bold")
    _wordmark(ax, 129, 83.2)

    _txt(ax, 30, 79.0, "VMware NSX-T", size=11.5, color=VMW, weight="bold")
    _txt(ax, 90, 79.0, "Cisco Secure Workload", size=11.5, color=NAVY, weight="bold")
    _txt(ax, 126, 79.0, "Notes", size=10.5, color=GREY, weight="bold")

    rows = [
        ("NSX Tag / VM attribute", "Label / annotation",
         "From vCenter, CMDB, DNS, ServiceNow, or CSV upload", GRN),
        ("Group (dynamic/static)", "Inventory filter / Scope",
         "Query on labels = dynamic membership", GRN),
        ("Security Policy + Category", "Workspace + policy priority",
         "Absolute / Default / Catch-all ordering", BLUE),
        ("DFW rule (src/dst/svc/action)", "Policy (consumer\u2192provider, port/proto)",
         "Allow/Deny; stateful", BLUE),
        ("Services (ports/protocols)", "Protocols & ports in policy",
         "Direct 1:1 mapping", BLUE),
        ("Applied To (scope limiter)", "Scope assignment",
         "CSW scopes bound enforcement", PURP),
        ("Context Profile \u2014 L7 App-ID", "Process + L4 context",
         "\u26a0 No DPI App-ID; use process/FQDN context", AMBER),
        ("Distributed IDS/IPS", "Forensics / behavior + Secure Firewall",
         "\u26a0 Not a 1:1 replacement (pair w/ NGFW)", RED),
        ("Identity Firewall (AD user)", "ISE integration (user/device)",
         "\u26a0 Via Cisco ISE context", AMBER),
    ]
    y = 74.0
    rh = 6.7
    for nsx, csw, note, col in rows:
        y -= rh
        _box(ax, 4, y, 52, rh - 1.1, VMW, VMWBG, lw=1.3, rounding=0.5)
        _txt(ax, 30, y + (rh - 1.1) / 2, nsx, size=8.0, color=VMW, weight="bold")
        _box(ax, 64, y, 52, rh - 1.1, col, "white", lw=1.5, rounding=0.5)
        _txt(ax, 90, y + (rh - 1.1) / 2, csw, size=8.0, color=col, weight="bold")
        _arrow(ax, (56.4, y + (rh - 1.1) / 2), (63.6, y + (rh - 1.1) / 2), col, lw=1.8, ms=13)
        _txt(ax, 118, y + (rh - 1.1) / 2, note, size=6.6, color=GREY, ha="left")

    # legend / gap banner
    _box(ax, 4, 4.0, 112, 6.2, AMBER, AMBBG, lw=1.6, rounding=0.7)
    _txt(ax, 7, 8.3, "\u26a0  Capability deltas to plan for:", size=8.4, color=AMBER, weight="bold", ha="left")
    _txt(ax, 7, 5.8,
         "L7 App-ID DPI \u00b7 Distributed IDS/IPS \u00b7 AD Identity FW are NOT direct CSW features \u2014 close with process context, FQDN policy, Cisco ISE, and Secure Firewall/Hypershield.",
         size=6.8, color=GREY, ha="left")
    _box(ax, 119, 4.0, 21, 6.2, GRN, GRNBG, lw=1.6, rounding=0.7)
    _txt(ax, 129.5, 8.3, "No import tool", size=7.6, color=GRN, weight="bold")
    _txt(ax, 129.5, 5.8, "map manually;\nADM accelerates", size=6.2, color=GREY)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    out = "nsx-to-csw-object-mapping.png"
    plt.savefig(out, dpi=100, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", out)


# =============================================================================
# Diagram 3 - phased migration timeline w/ coexistence lane
# =============================================================================
def diagram_phases():
    fig, ax = plt.subplots(figsize=(14.4, 8.8), dpi=100)
    ax.set_xlim(0, 144); ax.set_ylim(0, 88); ax.axis("off")

    _txt(ax, 60, 84.6, "NSX \u2192 CSW Migration \u2014 Phased, Risk-Managed Cutover",
         size=15.5, color=NAVY, weight="bold")
    _wordmark(ax, 129, 83.2)

    phases = [
        ("1", GRN,  "Discover", ["Deploy CSW agents in", "deep-visibility mode.", "Import vCenter tags", "as labels. Map flows."]),
        ("2", BLUE, "Model", ["Build scope tree to", "mirror NSX domains/", "tiers. NSX Groups", "\u2192 inventory filters."]),
        ("3", CYAN, "Translate", ["NSX DFW rules \u2192 CSW", "policies. Run ADM to", "auto-discover + fill", "gaps from real flows."]),
        ("4", PURP, "Analyze", ["Live policy analysis:", "compare policy vs", "observed flows.", "Fix misses/escapes."]),
        ("5", AMBER,"Parallel run", ["CSW agents enforce", "in monitor while NSX", "DFW still enforces.", "No double-deny."]),
        ("6", RED,  "Cutover", ["Per app/scope: enable", "CSW enforce, then", "remove matching NSX", "DFW rules."]),
        ("7", NAVY, "Decommission", ["All apps on CSW.", "Retire NSX DFW /", "reclaim NSX licenses.", "Operate in CSW."]),
    ]
    n = len(phases)
    x0, x1 = 8, 136
    step = (x1 - x0) / n
    # spine
    ax.add_patch(Rectangle((x0, 58.0), x1 - x0, 0.55, facecolor=BLUE, edgecolor="none", zorder=3))
    for i, (num, col, title, lines) in enumerate(phases):
        cx = x0 + step * i + step / 2
        ax.add_patch(FancyBboxPatch((cx - 1.4, 57.1), 2.8, 2.8, boxstyle="circle,pad=0",
                     linewidth=0, facecolor=col, zorder=5))
        _txt(ax, cx, 58.35, num, size=8.5, color="white", weight="bold", z=6)
        _box(ax, cx - 8.6, 61.5, 17.2, 15.5, col, "white", lw=1.5, rounding=0.7)
        _txt(ax, cx, 74.6, title, size=8.6, color=col, weight="bold")
        for j, ln in enumerate(lines):
            _txt(ax, cx, 71.4 - j * 2.3, ln, size=6.3, color=GREY)
        if i < n - 1:
            _arrow(ax, (cx + 8.8, 69), (cx + step - 8.8, 69), GREY, lw=1.2, ms=10, z=4)

    # ---- coexistence lanes (bottom) ----------------------------------------
    _txt(ax, 6, 50.4, "Enforcement owner over time", size=8.6, color=NAVY, weight="bold", ha="left")

    # NSX lane
    _box(ax, 8, 40, 128, 7.2, VMW, VMWBG, lw=1.4, rounding=0.5)
    _txt(ax, 4, 43.6, "NSX", size=7.6, color=VMW, weight="bold", ha="left")
    # NSX enforcing solid through phase 6, fading
    nsx_end = x0 + step * 6 + step * 0.5
    _box(ax, 9, 41, nsx_end - 9, 5.2, VMW, VMW, lw=0, rounding=0.4)
    _txt(ax, (9 + nsx_end) / 2, 43.6, "NSX DFW ENFORCING (authoritative)", size=7.4, color="white", weight="bold")
    _box(ax, nsx_end, 41, 135 - nsx_end, 5.2, VMW, "white", lw=1.2, rounding=0.4, ls="dashed")
    _txt(ax, (nsx_end + 135) / 2, 43.6, "retired", size=7.0, color=VMW, weight="bold")

    # CSW lane
    _box(ax, 8, 30.5, 128, 7.2, BLUE, BLUEBG, lw=1.4, rounding=0.5)
    _txt(ax, 4, 34.1, "CSW", size=7.6, color=BLUE, weight="bold", ha="left")
    mon_start = x0 + step * 0.5
    enf_start = x0 + step * 4 + step * 0.2
    _box(ax, mon_start, 31.5, enf_start - mon_start, 5.2, GRN, GRNBG, lw=1.2, rounding=0.4)
    _txt(ax, (mon_start + enf_start) / 2, 34.1, "CSW visibility / analysis (monitor)", size=7.2, color=GRN, weight="bold")
    _box(ax, enf_start, 31.5, 135 - enf_start, 5.2, BLUE, BLUE, lw=0, rounding=0.4)
    _txt(ax, (enf_start + 135) / 2, 34.1, "CSW ENFORCING (per-app \u2192 all)", size=7.4, color="white", weight="bold")

    # cutover marker
    cutx = (enf_start + nsx_end) / 2
    _arrow(ax, (cutx, 40), (cutx, 37.7), RED, lw=1.6, ms=12)
    _txt(ax, cutx + 3, 38.85, "per-app handoff (avoid double-enforcement)",
         size=6.2, color=RED, weight="bold", ha="left")

    # guardrails box
    _box(ax, 8, 6, 128, 20, NAVY, "white", lw=1.6, rounding=0.8)
    _txt(ax, 72, 23.2, "Migration guardrails", size=9.6, color=NAVY, weight="bold")
    left = [
        "\u2022 Never enforce the same app on NSX and CSW at once \u2014 cut over per app/scope.",
        "\u2022 Deploy agents deep-visibility-first; enforcement OFF until analysis is clean.",
        "\u2022 Import vCenter tags early so labels/filters mirror existing NSX Groups.",
        "\u2022 Use ADM + live analysis to catch flows NSX allowed implicitly.",
    ]
    right = [
        "\u2022 Keep a default-allow (or logging) baseline until per-app policy is proven.",
        "\u2022 Plan for gaps: L7 App-ID, Distributed IDS/IPS, AD Identity FW.",
        "\u2022 Roll back = disable CSW enforcement on that scope; NSX still owns it.",
        "\u2022 Decommission NSX DFW only after every app is enforced on CSW.",
    ]
    for i, ln in enumerate(left):
        _txt(ax, 10, 20.0 - i * 3.1, ln, size=7.0, color=INK, ha="left")
    for i, ln in enumerate(right):
        _txt(ax, 74, 20.0 - i * 3.1, ln, size=7.0, color=INK, ha="left")

    _gradient_bar(ax, 8, 2.6, 128, 0.9)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    out = "nsx-to-csw-migration-phases.png"
    plt.savefig(out, dpi=100, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    diagram_compare()
    diagram_mapping()
    diagram_phases()
