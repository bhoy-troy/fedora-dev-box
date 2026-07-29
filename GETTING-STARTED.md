# Getting Started with Fedora Dev Box

A containerized RHEL/Fedora development environment with Ansible-based configuration.

## Quick Start

```bash
# 1. Build the container (VPN required for Red Hat internal COPR repos)
docker-compose build

# 2. Start the container
docker-compose up -d

# 3. Enter the container
docker-compose exec toolbox bash

# 4. Inside container: Configure environment with Ansible
cd /projects/fedora-dev-box
ansible-playbook setup-all.yml

# 5. Start using tmux and development tools
tmux
```

## Running Ansible Playbooks

**IMPORTANT:** All Ansible playbooks run INSIDE the container to configure the container environment.

### Method 1: Interactive (Inside Container)

```bash
# Enter the container
docker-compose exec toolbox bash

# Navigate to project directory
cd /projects/fedora-dev-box

# Run individual playbooks
ansible-playbook setup-tmux.yml        # Configure tmux only
ansible-playbook setup-packages.yml    # Install packages only
ansible-playbook setup-all.yml         # Complete setup (recommended)

# Or use tags to run specific roles
ansible-playbook setup-all.yml --tags tmux    # Only tmux
ansible-playbook setup-all.yml --tags dnf     # Only packages
ansible-playbook setup-all.yml --tags all     # Everything (default)
```

### Method 2: One-liner from Host

```bash
# Execute playbook inside container without entering
docker-compose exec toolbox ansible-playbook /projects/fedora-dev-box/setup-all.yml

# With secrets file (for LDAP and certificate configuration)
docker-compose exec toolbox ansible-playbook /projects/fedora-dev-box/setup-all.yml --extra-vars @ansible/secrets.yml
```

## Available Playbooks

| Playbook | Description | What It Does |
|----------|-------------|--------------|
| `setup-certificates.yml` | CA certificates | Installs Red Hat root CA certificates |
| `setup-rcm-tools.yml` | RCM Tools repository | Configures Red Hat release tools repo |
| `setup-copr-repos.yml` | COPR repositories | Enables 7 COPR repos for dev tools |
| `setup-ldap.yml` | LDAP & authentication | Configures LDAP, Kerberos, SSH bastion |
| `setup-config.yml` | System configuration | Deploys profile scripts and utility commands |
| `setup-tmux.yml` | Tmux configuration | Installs tmux with vim keybindings, mouse support, custom status bar |
| `setup-packages.yml` | Development packages | Installs 46+ packages for RHEL/Fedora development |
| `setup-all.yml` | Complete setup | Runs all roles (certificates, rcm-tools, copr-repos, ldap, config, packages, tmux) |

## What Gets Installed

### CA Certificates
- Red Hat IT Root CA certificates (2015, 2022)
- Installed to `/etc/pki/ca-trust/source/anchors/`
- System CA trust store automatically updated

### RCM Tools Repository
- Red Hat Release Configuration Management tools repository
- GPG key: `/etc/pki/rpm-gpg/RPM-GPG-KEY-rcminternal`
- Repository: `/etc/yum.repos.d/rcm-tools-fedora.repo`
- Provides internal release engineering tools

### COPR Repositories
- 7 COPR repos enabled for development tools
- Internal Red Hat COPR (requires VPN): osh, qa-tools, toolset, beaker, etc.
- Public COPR: dev-toolbox-extras
- Provides: osh-client, rhel-repoquery, rhelbz-components, and more

### LDAP & Authentication
- LDAP configuration: `/etc/openldap/ldap.conf`
  - Red Hat internal LDAP client settings
- Kerberos configuration: `/etc/krb5.conf.d/ipa_redhat_com`
  - IPA realm configuration for GSSAPI
- SSH bastion: `/etc/ssh/ssh_config.d/00-distgit-bastion.conf`
  - Automatic dist-git bastion routing via ProxyJump
  - GSSAPI authentication
  - LDAP-based known hosts lookup

### System Configuration
- Profile script at `/etc/profile.d/rhel_dev_toolbox.sh`
  - Host command aliases for ostree systems
  - Toolbox-vscode integration tweaks
- Utility scripts at `/usr/libexec/rhel-developer-toolbox/`
  - `rdtx-check-config` - Configuration validation
  - `rdtx_bind_mounts` - Bind mount management

### Tmux Configuration
- Mouse support enabled
- Vim-style navigation (h/j/k/l)
- Custom status bar with date/time
- 10,000 line scrollback
- Better split keybindings: `|` (vertical), `-` (horizontal)
- Config reload: `prefix + r`

### Development Packages (45+)

**Packager Tools:**
- fedora-packager, rhel-packager, centos-packager
- fedpkg, rhpkg, centpkg
- rpmdevtools, rpm-build

**Build Tools:**
- argbash, bison, flex
- scl-utils, scl-utils-build

**Testing & CI:**
- beaker-client, beaker-redhat
- tmt-all, tmt-redhat-all
- csmock, csdiff

**Container & Virtualization:**
- podman-remote (connects to host Podman)
- skopeo
- libvirt-client, virt-manager, virt-viewer

**Development Utilities:**
- vim, nano, zsh
- git-subtree, glab
- jq, yamllint
- powerline-go

**Specialized Tools:**
- osh-client (covscan)
- rhcopr (COPR client)
- koji-osbuild-cli
- rhel-repoquery, rhelbz-components

## Container Management

### Common Commands

```bash
# Start container
docker-compose up -d

# Stop container
docker-compose down

# Restart container
docker-compose restart

# View logs
docker-compose logs -f

# Enter container
docker-compose exec toolbox bash

# Run single command in container
docker-compose exec toolbox <command>
```

### Using Host Podman

The container shares your host's Podman socket, so you can manage host containers from inside:

```bash
# Inside container
podman ps              # List host containers
podman images          # List host images
podman run ...         # Run containers on host
podman build ...       # Build images on host
```

No nested containerization needed!

## Code Quality Analysis

The dev box includes SonarQube and CodeClimate (qlty) for static code analysis.

### SonarQube

**Access the web UI:**
- URL: http://localhost:9000
- Default credentials: `admin` / `admin` (change on first login)
- Services: PostgreSQL database + SonarQube server

**Run analysis from toolbox:**
```bash
# Inside container
cd /projects/your-project

# Run sonar-scanner
sonar-scanner \
  -Dsonar.projectKey=your-project \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://sonarqube:9000 \
  -Dsonar.login=<your-token>
```

**Get analysis token:**
1. Login to http://localhost:9000
2. Go to My Account → Security → Generate Token
3. Use token in sonar-scanner command

### CodeClimate (qlty)

**Run analysis from toolbox:**
```bash
# Inside container
cd /projects/your-project

# Run qlty analyze
codeclimate analyze

# Output JSON report
codeclimate analyze --format json > report.json
```

**Configure analysis:**
Create `.codeclimate.yml` in your project:
```yaml
version: "2"
plugins:
  shellcheck:
    enabled: true
  yamllint:
    enabled: true
  pylint:
    enabled: true
exclude_patterns:
  - "**/*.pyc"
  - ".git/"
```

### Service Management

```bash
# Check service status
docker-compose ps

# View SonarQube logs
docker-compose logs -f sonarqube

# Restart services
docker-compose restart sonarqube postgres

# Stop services
docker-compose down
```

**Note:** SonarQube takes ~2 minutes to start on first run.

## Directory Structure

```
Inside Container:
/projects/fedora-dev-box/     # Your project (mounted from host)
├── setup-tmux.yml            # Run these playbooks
├── setup-packages.yml
├── setup-all.yml
└── ansible/
    └── roles/                # Ansible roles
        ├── tmux/
        └── dnf-packages/

/usr/share/rhel-dev-toolbox/  # Baked-in configs
└── ansible/                  # Alternative playbook location
```

## Development Workflow

1. **Build once:** `docker-compose build` (requires VPN)
2. **Start container:** `docker-compose up -d`
3. **Configure once:** Run `ansible-playbook setup-all.yml` inside container
4. **Daily use:** `docker-compose exec toolbox bash` to enter
5. **Iterate:** Modify Ansible roles, re-run playbooks (no rebuild needed)

## Using Secrets File

The `ansible/secrets.yml` file centralizes sensitive configuration like LDAP settings and certificate paths.

**Basic usage (unencrypted):**
```bash
cd /projects/fedora-dev-box
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

**With Ansible Vault (encrypted):**
```bash
# Encrypt the secrets file
ansible-vault encrypt ansible/secrets.yml

# Edit encrypted file
ansible-vault edit ansible/secrets.yml

# Use encrypted file
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml --ask-vault-pass
```

**What's in secrets.yml:**
- LDAP server URIs and configuration
- CA certificate content (inline PEM format)
- Other sensitive configuration

**Note:** Certificates are stored as inline content in secrets.yml, not as separate files.

## Customization

### Add Extra Packages

Create a custom playbook:

```yaml
---
# my-setup.yml
- name: Custom environment setup
  hosts: all
  roles:
    - role: dnf-packages
      dnf_extra_packages:
        - golang
        - rust
        - nodejs
    - role: tmux
```

Run it: `ansible-playbook my-setup.yml`

### Modify Tmux Config

Edit `ansible/roles/tmux/files/tmux.conf` and re-run:
```bash
ansible-playbook setup-tmux.yml
```

### Create New Role

```bash
cd ansible/roles
mkdir -p my-role/{tasks,files,defaults}
# Create tasks/main.yml
# Add to setup-all.yml
```

## Troubleshooting

### Build Error: "Could not resolve host: copr.devel.redhat.com"
**Cause:** Not connected to Red Hat VPN  
**Solution:** Connect to VPN and retry `docker-compose build`

### Ansible Command Not Found
**Cause:** Not inside container or Ansible not installed  
**Solution:** Enter container first: `docker-compose exec toolbox bash`

### Podman Commands Don't Work in Container
**Cause:** Host Podman not running or socket not mounted  
**Solution:**
```bash
# On host
podman machine list
podman machine start

# Verify socket mount
docker-compose exec toolbox ls -la /run/podman/podman.sock
```

### Playbook Fails with Permission Denied
**Cause:** Some tasks require sudo  
**Solution:** Ansible config has `become = True` by default, ensure sudo works in container

## Next Steps

After setup:
1. Test tmux: `tmux`
2. Test podman: `podman ps`
3. Start development: `cd /projects/fedora-dev-box`
4. Build packages: `fedpkg clone <package> && cd <package> && fedpkg mockbuild`

## More Information

- Ansible roles: `ansible/README.md`
- Upstream docs: `rhel-developer-toolbox/README.md`
- Dockerfile: `images/Dockerfile.base`
