# RCM Tools Role

Configures Red Hat Release Configuration Management (RCM) Tools repository.

## Description

This role sets up the RCM Tools repository for accessing Red Hat internal release engineering tools. The repository provides tools used for building, releasing, and managing Red Hat products.

**Note:** The default repository URL uses HTTPS. Configure the base URL in `secrets.yml` for your organization's requirements.

## What It Installs

1. **GPG Key** (`/etc/pki/rpm-gpg/RPM-GPG-KEY-rcminternal`)
   - GPG key for package verification (content from `secrets.yml`)

2. **Repository Configuration** (`/etc/yum.repos.d/rcm-tools-fedora.repo`)
   - RCM Tools repository for Fedora
   - Configured with base URL from `secrets.yml`

## Tags

`all`, `rcm-tools`

## Variables

### `rcm_tools_enabled`

Enable or disable RCM Tools repository configuration.

**Default:** `true`

**To disable:**
```yaml
rcm_tools_enabled: false
```

### `rcm_tools_baseurl`

Base URL for the RCM Tools repository.

**Default:** `https://download.engineering.redhat.com/rel-eng/RCMTOOLS/latest-RCMTOOLS-2-F-$releasever/compose/Everything/$basearch/os/`

**Note:** Override in `secrets.yml` for your organization's repository URL.

**Example custom URL:**
```yaml
rcm_tools_baseurl: "https://your-mirror.example.com/rcmtools/$releasever/$basearch/"
```

The URL can contain DNF/YUM variables:
- `$releasever` - Fedora release version
- `$basearch` - System architecture (x86_64, aarch64, etc.)

### `rcm_tools_gpg_key`

GPG public key content for package verification.

**Default:** Example placeholder key (must be overridden in `secrets.yml`)

**Note:** Provide the full GPG public key block in `secrets.yml`.

**Example in `secrets.yml`:**
```yaml
rcm_tools_gpg_key: |
  -----BEGIN PGP PUBLIC KEY BLOCK-----
  Version: GnuPG v2.0.22 (GNU/Linux)

  mQINBFO+epgBEADNQEdzLIB...
  ...
  -----END PGP PUBLIC KEY BLOCK-----
```

**To export a GPG key for use:**
```bash
gpg --armor --export KEY_ID > gpg-key.asc
```

## Files Deployed

| Source | Destination | Purpose |
|--------|-------------|---------|
| `rcm_tools_gpg_key` (variable) | `/etc/pki/rpm-gpg/RPM-GPG-KEY-rcminternal` | GPG key from secrets.yml |
| `rcm-tools-fedora.repo.j2` | `/etc/yum.repos.d/rcm-tools-fedora.repo` | Repository config (templated from secrets.yml) |

## Example Playbook

### Basic Usage (with secrets.yml)

```yaml
---
- name: Configure RCM Tools repository
  hosts: all
  roles:
    - role: rcm-tools
```

**Configure in `secrets.yml`:**
```yaml
# RCM Tools repository base URL
rcm_tools_baseurl: "https://download.engineering.redhat.com/rel-eng/RCMTOOLS/latest-RCMTOOLS-2-F-$releasever/compose/Everything/$basearch/os/"

# RCM Tools GPG key
rcm_tools_gpg_key: |
  -----BEGIN PGP PUBLIC KEY BLOCK-----
  Version: GnuPG v2.0.22 (GNU/Linux)
  
  mQINBFO+epgBEADNQEdzLIB...
  ...
  -----END PGP PUBLIC KEY BLOCK-----
```

**Run playbook:**
```bash
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

### Custom Repository URL (inline)

```yaml
---
- name: Configure with custom RCM Tools repository
  hosts: all
  roles:
    - role: rcm-tools
      rcm_tools_baseurl: "https://your-mirror.example.com/rcmtools/$releasever/$basearch/"
```

### Skip RCM Tools

```yaml
---
- name: Setup without RCM Tools
  hosts: all
  roles:
    - role: rcm-tools
      rcm_tools_enabled: false
```

Or use tags:
```bash
ansible-playbook setup-all.yml --skip-tags rcm-tools
```

## Dependencies

None

## Usage After Configuration

Once the role is applied, you can install RCM tools packages:

```bash
# Search for available tools
dnf search rcm

# Example: Install a package from RCM Tools
dnf install <package-name>

# List enabled repositories
dnf repolist
```

## Notes

- Requires connection to Red Hat internal network (VPN) for default URL
- Repository URL is configurable via `rcm_tools_baseurl` in `secrets.yml`
- GPG key verification is enforced for package security
- The default repository provides internal Red Hat release engineering tools
- Default repository is internal to Red Hat and not available externally
- Repository configuration is templated to allow organization-specific URLs

## Security

Package integrity is maintained through:
- GPG signature verification on all packages (key stored in `secrets.yml`)
- Internal network access requirement (for Red Hat internal repository)
- Controlled access to repository content
- HTTPS support for repository URL (recommended)
- GPG key and repository URL can be encrypted with `ansible-vault`

## Troubleshooting

### Repository not accessible

```bash
# Check VPN connection (for Red Hat internal repository)
curl -I https://download.engineering.redhat.com/

# Verify repository file and configured URL
cat /etc/yum.repos.d/rcm-tools-fedora.repo

# Test repository
dnf repolist --verbose

# Check if URL is reachable
curl -I "$(grep baseurl /etc/yum.repos.d/rcm-tools-fedora.repo | cut -d= -f2 | head -n1)"
```

**If repository URL needs to be changed:**
- Update `rcm_tools_baseurl` in `secrets.yml`
- Re-run the Ansible playbook

### GPG key issues

```bash
# Verify key installation
ls -la /etc/pki/rpm-gpg/RPM-GPG-KEY-rcminternal

# View installed key content
cat /etc/pki/rpm-gpg/RPM-GPG-KEY-rcminternal

# Check key is imported by RPM
rpm -qa gpg-pubkey*

# Import key manually if needed
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-rcminternal
```

**If GPG key needs to be changed:**
- Update `rcm_tools_gpg_key` in `secrets.yml`
- Re-run the Ansible playbook
- Reimport the key: `rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-rcminternal`

### Disable repository temporarily

```bash
# Disable for single command
dnf install --disablerepo=rcm-tools <package>

# Or disable in repo file
dnf config-manager --set-disabled rcm-tools
```
