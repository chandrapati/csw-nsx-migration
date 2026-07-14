#!/usr/bin/env python3
"""Export VMware NSX-T DFW objects to CSV to seed a Cisco Secure Workload migration.

Pulls Groups, Security Policies + Distributed Firewall rules, and Services from the
NSX-T **Policy API** and writes flat CSVs you can use to build the CSW label / filter /
policy mapping (see ../docs/NSX-to-CSW-MAPPING-CHEATSHEET.md).

This is a **read-only** discovery helper. It never modifies NSX and never writes
credentials to disk.

Security notes:
  * Credentials come ONLY from environment variables or an interactive prompt —
    never hardcode them and never pass them on the command line.
  * TLS certificate verification is ON by default. Use --insecure only in a lab,
    and prefer --ca-bundle <path> to trust a private CA in production.

Usage:
  export NSX_MANAGER="nsxmgr.example.com"
  export NSX_USER="svc-nsx-ro"
  export NSX_PASSWORD="..."          # or omit to be prompted
  python3 nsx_export.py --out-dir ./nsx-export

Requires: requests  (pip install requests)
"""
from __future__ import annotations

import argparse
import csv
import getpass
import os
import sys
from urllib.parse import quote

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    sys.exit("This script needs 'requests'. Install with: pip install requests")


class NsxClient:
    """Minimal read-only NSX-T Policy API client with pagination."""

    def __init__(self, host: str, auth: HTTPBasicAuth, verify, timeout: int = 30):
        # Accept a bare hostname or a full URL; normalize to https base.
        host = host.strip().rstrip("/")
        if host.startswith("http://"):
            raise ValueError("Refusing plaintext HTTP; NSX Policy API must be HTTPS.")
        if not host.startswith("https://"):
            host = "https://" + host
        self.base = host
        self.session = requests.Session()
        self.session.auth = auth
        self.session.headers.update({"Accept": "application/json"})
        self.verify = verify
        self.timeout = timeout

    def get(self, path: str) -> dict:
        url = f"{self.base}{path}"
        resp = self.session.get(url, verify=self.verify, timeout=self.timeout)
        if resp.status_code == 401:
            raise SystemExit("NSX auth failed (401). Check NSX_USER / NSX_PASSWORD.")
        resp.raise_for_status()
        return resp.json()

    def get_all(self, path: str) -> list:
        """Follow NSX 'cursor' pagination and return the combined results list."""
        results: list = []
        cursor = None
        while True:
            sep = "&" if "?" in path else "?"
            page = path if cursor is None else f"{path}{sep}cursor={quote(cursor)}"
            data = self.get(page)
            results.extend(data.get("results", []))
            cursor = data.get("cursor")
            if not cursor or not data.get("results"):
                break
        return results


def _short(path_ref: str) -> str:
    """Turn a policy path like /infra/domains/default/groups/web into its last id."""
    return path_ref.rsplit("/", 1)[-1] if path_ref else path_ref


def _join(items) -> str:
    return " | ".join(_short(i) for i in items) if items else ""


def export_groups(client: NsxClient, domain: str, out_dir: str) -> int:
    groups = client.get_all(f"/policy/api/v1/infra/domains/{quote(domain)}/groups")
    path = os.path.join(out_dir, "nsx_groups.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["group_id", "display_name", "criteria_or_members",
                    "csw_label_hint", "csw_filter_hint"])
        for g in groups:
            gid = g.get("id", "")
            name = g.get("display_name", gid)
            crit = []
            for expr in g.get("expression", []) or []:
                rt = expr.get("resource_type", "")
                if rt == "Condition":
                    crit.append(f"{expr.get('member_type')}."
                                f"{expr.get('key')} {expr.get('operator')} "
                                f"'{expr.get('value')}'")
                elif rt == "IPAddressExpression":
                    crit.append("IPs: " + _join(expr.get("ip_addresses", [])))
                elif rt == "PathExpression":
                    crit.append("members: " + _join(expr.get("paths", [])))
                elif rt == "ConjunctionOperator":
                    crit.append(expr.get("conjunction_operator", "AND"))
            w.writerow([gid, name, " ; ".join(crit),
                        f"label: app={name}", f"filter: name contains {name}"])
    print(f"  wrote {path}  ({len(groups)} groups)")
    return len(groups)


def export_policies(client: NsxClient, domain: str, out_dir: str) -> int:
    policies = client.get_all(
        f"/policy/api/v1/infra/domains/{quote(domain)}/security-policies")
    path = os.path.join(out_dir, "nsx_dfw_rules.csv")
    rule_count = 0
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["security_policy", "category", "csw_priority_hint", "rule_id",
                    "rule_name", "source_groups", "destination_groups", "services",
                    "l7_context_profiles", "action", "direction", "applied_to",
                    "logged", "disabled"])
        cat_to_priority = {
            "Ethernet": "Absolute", "Emergency": "Absolute",
            "Infrastructure": "Absolute", "Environment": "Default",
            "Application": "Default",
        }
        for p in policies:
            pol_name = p.get("display_name", p.get("id", ""))
            category = p.get("category", "")
            priority = cat_to_priority.get(category, "Default")
            for r in p.get("rules", []) or []:
                rule_count += 1
                w.writerow([
                    pol_name, category, priority,
                    r.get("id", ""), r.get("display_name", ""),
                    _join(r.get("source_groups", [])),
                    _join(r.get("destination_groups", [])),
                    _join(r.get("services", [])),
                    _join(r.get("profiles", [])),
                    r.get("action", ""),
                    r.get("direction", "IN_OUT"),
                    _join(r.get("scope", [])),
                    str(r.get("logged", False)).lower(),
                    str(r.get("disabled", False)).lower(),
                ])
    print(f"  wrote {path}  ({len(policies)} policies, {rule_count} rules)")
    return rule_count


def export_services(client: NsxClient, out_dir: str) -> int:
    services = client.get_all("/policy/api/v1/infra/services")
    path = os.path.join(out_dir, "nsx_services.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["service_id", "display_name", "l4_protocol", "ports"])
        for s in services:
            for entry in s.get("service_entries", []) or []:
                w.writerow([
                    s.get("id", ""), s.get("display_name", ""),
                    entry.get("l4_protocol", entry.get("resource_type", "")),
                    _join(entry.get("destination_ports", [])),
                ])
    print(f"  wrote {path}  ({len(services)} services)")
    return len(services)


def parse_args(argv=None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=os.environ.get("NSX_MANAGER"),
                    help="NSX Manager hostname/FQDN (or set NSX_MANAGER).")
    ap.add_argument("--domain", default="default",
                    help="NSX policy domain (default: 'default').")
    ap.add_argument("--out-dir", default="nsx-export",
                    help="Directory to write CSVs (default: ./nsx-export).")
    ap.add_argument("--ca-bundle", default=os.environ.get("NSX_CA_BUNDLE"),
                    help="Path to a CA bundle to verify the NSX cert (recommended).")
    ap.add_argument("--insecure", action="store_true",
                    help="Disable TLS verification (LAB ONLY).")
    ap.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds.")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if not args.host:
        sys.exit("Provide --host or set NSX_MANAGER.")

    user = os.environ.get("NSX_USER") or input("NSX username: ").strip()
    password = os.environ.get("NSX_PASSWORD") or getpass.getpass("NSX password: ")
    if not user or not password:
        sys.exit("NSX credentials are required (NSX_USER / NSX_PASSWORD).")

    if args.insecure:
        verify = False
        print("WARNING: TLS verification disabled (--insecure). Do not use in prod.",
              file=sys.stderr)
        try:
            requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
        except Exception:
            pass
    else:
        verify = args.ca_bundle if args.ca_bundle else True

    os.makedirs(args.out_dir, exist_ok=True)

    try:
        client = NsxClient(args.host, HTTPBasicAuth(user, password), verify,
                           timeout=args.timeout)
        print(f"Exporting from {client.base} (domain='{args.domain}') ...")
        export_groups(client, args.domain, args.out_dir)
        export_policies(client, args.domain, args.out_dir)
        export_services(client, args.out_dir)
    except requests.exceptions.SSLError as e:
        sys.exit(f"TLS error talking to NSX: {e}\n"
                 "Use --ca-bundle <path> to trust a private CA, or --insecure in a lab.")
    except requests.exceptions.RequestException as e:
        sys.exit(f"NSX request failed: {e}")

    print(f"Done. CSVs in '{args.out_dir}/'. Next: map into CSW labels/filters/policies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
