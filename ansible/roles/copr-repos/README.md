# COPR Repositories Role

Enables COPR (Cool Other Package Repositories) for RHEL and Fedora development tools.

## Description

This role enables a set of COPR repositories that provide useful development tools not available in standard Fedora repositories. COPR is a build system for creating and hosting RPM packages.

**Repositories should be configured in `secrets.yml`.**

**Common Red Hat internal repositories:**

1. **@osh/osh-prod** (copr.devel.redhat.com)
   - OSH (Open Source Hub) production tools
   - Formerly known as covscan

2. **lpol/qa-tools** (copr.devel.redhat.com)
   - Quality assurance and testing tools

3. **rhcopr-project/toolset** (copr.devel.redhat.com)
   - Red Hat COPR project toolset

4. **@kernel-maintainers/beaker-redhat** (copr.devel.redhat.com)
   - Beaker testing framework for Red Hat

5. **petersen/rhel-repoquery** (copr.devel.redhat.com)
   - RHEL repository query tools

6. **petersen/rhelbz-components** (copr.devel.redhat.com)
   - RHEL Bugzilla component tools

7. **sgallagh/dev-toolbox-extras** (copr.fedorainfracloud.org)
   - Additional developer toolbox utilities

## Tags

`all`, `copr-repos`

## Variables

### `copr_repositories`

List of COPR repositories to enable.

**Default:** `[]` (empty list - configure in `secrets.yml`)

**NOTE:** Override this in `secrets.yml` with your organization's repositories.

**Example configuration in `secrets.yml`:**
```yaml
copr_repositories:
  - "copr.devel.redhat.com/@osh/osh-prod"
  - "copr.devel.redhat.com/lpol/qa-tools"
  - "copr.devel.redhat.com/rhcopr-project/toolset"
  - "copr.devel.redhat.com/@kernel-maintainers/beaker-redhat"
  - "copr.devel.redhat.com/petersen/rhel-repoquery"
  - "copr.devel.redhat.com/petersen/rhelbz-components"
  - "sgallagh/dev-toolbox-extras"
```

**Format:**
- Full: `"host/owner/project"`
- Short: `"owner/project"` (uses default copr.fedorainfracloud.org)

**Custom repositories:**
```yaml
copr_repositories:
  - "copr.devel.redhat.com/@osh/osh-prod"
  - "myusername/myproject"  # Uses copr.fedorainfracloud.org
```

**Disable all COPR repos:**
```yaml
copr_repositories: []
```

## Files Deployed

This role does not deploy files directly. It uses `dnf copr enable` to configure repositories in `/etc/yum.repos.d/`.

**Generated repository files (examples):**
- `/etc/yum.repos.d/_copr:copr.devel.redhat.com:group_osh:osh-prod.repo`
- `/etc/yum.repos.d/_copr:copr.devel.redhat.com:lpol:qa-tools.repo`
- etc.

## Example Playbook

### Basic Usage (with secrets.yml)

```yaml
---
- name: Enable COPR repositories
  hosts: all
  roles:
    - role: copr-repos
```

**Configure repositories in `secrets.yml`:**
```yaml
copr_repositories:
  - "copr.devel.redhat.com/@osh/osh-prod"
  - "copr.devel.redhat.com/lpol/qa-tools"
  - "sgallagh/dev-toolbox-extras"
```

**Run playbook:**
```bash
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

### Custom Repositories (inline)

```yaml
---
- name: Enable custom COPR repositories
  hosts: all
  roles:
    - role: copr-repos
      copr_repositories:
        - "copr.devel.redhat.com/@osh/osh-prod"
        - "username/custom-tools"
```

### Skip COPR Repositories

Set empty list in `secrets.yml`:
```yaml
copr_repositories: []
```

Or use tags:
```bash
ansible-playbook setup-all.yml --skip-tags copr-repos
```

## Dependencies

- `dnf-plugins-core` package (usually pre-installed on Fedora)

## Usage After Configuration

Once repositories are enabled, packages from COPR become available:

```bash
# List enabled repositories
dnf repolist | grep copr

# Search for packages from COPR
dnf search osh-client
dnf search rhel-repoquery

# Install packages from COPR
dnf install osh-client
dnf install rhel-repoquery rhelbz-components

# Disable a COPR repository
dnf copr disable copr.devel.redhat.com/@osh/osh-prod

# Remove a COPR repository
dnf copr remove copr.devel.redhat.com/@osh/osh-prod
```

## Notes

- **Red Hat internal COPR** (copr.devel.redhat.com) requires VPN connection
- **Public COPR** (copr.fedorainfracloud.org) is publicly accessible
- COPR repositories are community-maintained and not officially supported
- Packages from COPR may have different quality levels than official Fedora packages
- The role is idempotent - re-running won't fail if repos are already enabled

## Security Considerations

- COPR packages are built by third parties
- Red Hat internal COPR (copr.devel.redhat.com) is more trusted than public COPR
- All packages are GPG signed and verified by default
- Review repository contents before enabling:
  ```bash
  dnf copr list <owner>
  ```

## Troubleshooting

### Repository not accessible

```bash
# Check VPN for internal COPR
ping copr.devel.redhat.com

# Test public COPR
ping copr.fedorainfracloud.org

# Verify repository files
ls -la /etc/yum.repos.d/*copr*
```

### Enable failed

```bash
# Check if dnf-plugins-core is installed
dnf install dnf-plugins-core

# Try manual enable
dnf copr enable copr.devel.redhat.com/@osh/osh-prod

# Check repository metadata
dnf repolist --verbose
```

### Repository conflicts

```bash
# Disable problematic repository
dnf copr disable <repository>

# Or disable temporarily
dnf install --disablerepo=<copr-repo> <package>
```

## COPR Repository Information

| Repository | Host | Purpose | Access |
|------------|------|---------|--------|
| @osh/osh-prod | copr.devel.redhat.com | Code scanning tools | VPN required |
| lpol/qa-tools | copr.devel.redhat.com | QA testing tools | VPN required |
| rhcopr-project/toolset | copr.devel.redhat.com | COPR utilities | VPN required |
| @kernel-maintainers/beaker-redhat | copr.devel.redhat.com | Beaker testing | VPN required |
| petersen/rhel-repoquery | copr.devel.redhat.com | Repo query tools | VPN required |
| petersen/rhelbz-components | copr.devel.redhat.com | Bugzilla tools | VPN required |
| sgallagh/dev-toolbox-extras | copr.fedorainfracloud.org | Extra dev tools | Public |

## References

- [COPR Documentation](https://docs.pagure.org/copr.copr/)
- [Fedora COPR](https://copr.fedorainfracloud.org/)
- [Red Hat Internal COPR](https://copr.devel.redhat.com/)
