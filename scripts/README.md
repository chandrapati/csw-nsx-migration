# NSX discovery scripts

Read-only helpers that export VMware NSX-T DFW objects so you can seed the CSW mapping
(see [`../docs/NSX-to-CSW-MAPPING-CHEATSHEET.md`](../docs/NSX-to-CSW-MAPPING-CHEATSHEET.md)).

## `nsx_export.py`

Pulls **Groups**, **Security Policies + DFW rules**, and **Services** from the NSX-T
**Policy API** and writes three CSVs.

### Install

```bash
pip install requests
```

### Run

```bash
export NSX_MANAGER="nsxmgr.example.com"
export NSX_USER="svc-nsx-ro"          # a read-only service account
export NSX_PASSWORD="..."             # or omit to be prompted securely
python3 nsx_export.py --out-dir ./nsx-export
```

Trust a private CA (recommended in production):

```bash
python3 nsx_export.py --ca-bundle /path/to/nsx-ca.pem
```

Lab only (skip TLS verification):

```bash
python3 nsx_export.py --insecure
```

### Output

| File | Contents | Seeds in CSW |
|---|---|---|
| `nsx_groups.csv` | Group id, name, criteria/members | Labels + inventory filters |
| `nsx_dfw_rules.csv` | Policy, category, rule, src/dst groups, services, L7 profiles, action, applied-to | Workspaces + policies (with priority hint) |
| `nsx_services.csv` | Service id, name, protocol, ports | Protocols & ports |

Each CSV includes hint columns (e.g. `csw_priority_hint`, `csw_filter_hint`) to speed translation.

### Security

- **No hardcoded credentials.** Creds come from env vars or an interactive prompt; nothing is written to disk.
- **TLS verification is ON by default.** Prefer `--ca-bundle`; `--insecure` is for labs only.
- Use a **read-only** NSX account.
- Exported CSVs may contain customer topology — they are **git-ignored** (`nsx-export/`, `*.csv`). Don't commit them.
