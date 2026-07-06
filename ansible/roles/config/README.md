# Config Role

Configures RHEL Developer Toolbox system files including profile scripts and utility commands.

## Description

This role sets up essential system configuration files for the RHEL Developer Toolbox:

1. **Profile script** (`/etc/profile.d/rhel_dev_toolbox.sh`)
   - Sets up aliases for interacting with host commands on ostree systems
   - Provides necessary tweaks for toolbox-vscode integration

2. **Utility scripts** (`/usr/libexec/rhel-developer-toolbox/`)
   - `rdtx-check-config` - Configuration validation utility
   - `rdtx_bind_mounts` - Bind mount management utility

**Note:** LDAP, Kerberos, and SSH bastion configurations have been moved to the `ldap` role.

## Tags

`all`, `config`

## Variables

### `rdtx_libexec_dir`
Directory for RHEL developer toolbox utilities.  
Default: `/usr/libexec/rhel-developer-toolbox`

## Files Deployed

| Source | Destination | Purpose |
|--------|-------------|---------|
| `rhel_dev_toolbox.sh` | `/etc/profile.d/rhel_dev_toolbox.sh` | Host command aliases and toolbox-vscode tweaks |
| `rdtx-check-config.py` | `/usr/libexec/rhel-developer-toolbox/rdtx-check-config` | Configuration checker |
| `rdtx_bind_mounts.py` | `/usr/libexec/rhel-developer-toolbox/rdtx_bind_mounts` | Bind mount manager |

## Example Playbook

### Basic Usage

```yaml
---
- name: Configure RHEL Developer Toolbox
  hosts: all
  roles:
    - role: config
```

### With Custom LDAP Settings

```yaml
---
- name: Configure with custom LDAP
  hosts: all
  roles:
    - role: config
      ldap_uri: "ldaps://ldap1.example.com/ ldaps://ldap2.example.com/"
      ldap_base: "dc=example,dc=com"
      ldap_sasl_mech: "GSSAPI"
```

### Using Secrets File

Create `secrets.yml`:
```yaml
---
ldap_uri: "ldaps://ldap1.internal.example.com/"
ldap_base: "dc=internal,dc=example,dc=com"
```

Encrypt with Ansible Vault:
```bash
ansible-vault encrypt secrets.yml
```

Use in playbook:
```bash
ansible-playbook setup-config.yml --extra-vars @secrets.yml --ask-vault-pass
```

## Dependencies

None

## Notes

- All files are deployed with proper ownership (root:root)
- Utility scripts are executable (0755)
- Profile script is sourced automatically on shell startup
- Creates `/usr/libexec/rhel-developer-toolbox/` if it doesn't exist



ansible-playbook playbooks/setup-tmux.yml