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

3. **XDG-open configuration**
   - Redirects xdg-open to use flatpak-xdg-open for host integration
   - Supports alternatives or DNF action methods

4. **Platform Python symlink** (`/usr/libexec/platform-python`)
   - Compatibility symlink for building RHEL-8 kernel sources on modern systems
   - Points to `/usr/bin/python3`

**Note:** LDAP, Kerberos, and SSH bastion configurations have been moved to the `ldap` role.

## Tags

`all`, `config`

## Variables

### `rdtx_libexec_dir`
Directory for RHEL developer toolbox utilities.  
Default: `/usr/libexec/rhel-developer-toolbox`

### `xdg_open_method`
Method for configuring xdg-open to work with the host system.

**Options:**
- `'alternatives'` (default, recommended) - Use alternatives system to point xdg-open to flatpak-xdg-open
- `'dnf-action'` - Use DNF action to redirect (original upstream hack)
- `'none'` - Don't configure xdg-open

**Default:** `'alternatives'`

**Why this is needed:** In a toolbox container, `xdg-open` should open files/URLs on the host system, not inside the container. The `flatpak-xdg-open` utility handles this via dbus.

**Recommended approach (alternatives):**
```yaml
xdg_open_method: 'alternatives'
```

**Original approach (DNF action):**
```yaml
xdg_open_method: 'dnf-action'
```

## RHEL-8 Kernel Build Compatibility

The role creates a symlink `/usr/libexec/platform-python` → `/usr/bin/python3` to enable building RHEL-8 kernel sources on modern systems.

**Why this is needed:** RHEL-8 kernel build scripts expect `platform-python`, which doesn't exist on modern Fedora systems. The symlink provides compatibility without requiring the actual platform-python package.

## Files Deployed

| Source | Destination | Purpose | When |
|--------|-------------|---------|------|
| `rhel_dev_toolbox.sh` | `/etc/profile.d/rhel_dev_toolbox.sh` | Host command aliases and toolbox-vscode tweaks | Always |
| `rdtx-check-config.py` | `/usr/libexec/rhel-developer-toolbox/rdtx-check-config` | Configuration checker | Always |
| `rdtx_bind_mounts.py` | `/usr/libexec/rhel-developer-toolbox/rdtx_bind_mounts` | Bind mount manager | Always |
| `xdg-open.actions` | `/etc/dnf/libdnf5-plugins/actions.d/xdg-open.actions` | DNF action to redirect xdg-open | `xdg_open_method == 'dnf-action'` |

## Symlinks Created

| Source | Destination | Purpose |
|--------|-------------|---------|
| `/usr/bin/python3` | `/usr/libexec/platform-python` | RHEL-8 kernel build compatibility |
| `/usr/bin/flatpak-xdg-open` | `/usr/local/bin/xdg-open` | Host xdg-open integration (when using alternatives) |

**Note:** When `xdg_open_method == 'alternatives'`, the alternatives system is used instead of deploying files.

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