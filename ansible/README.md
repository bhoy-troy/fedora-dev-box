# Ansible Playbooks and Roles

This directory contains Ansible playbooks and roles for configuring the RHEL Developer Toolbox container.

## Structure

```
ansible/
├── ansible.cfg           # Ansible configuration
├── inventory            # Inventory file
├── playbooks/           # Playbooks
│   └── setup-tmux.yml
└── roles/              # Roles
    └── tmux/           # Tmux configuration role
        ├── defaults/
        ├── files/
        ├── tasks/
        └── templates/
```

## Usage

**IMPORTANT:** These playbooks are designed to run INSIDE the container to configure the container environment.

### Running Inside Container

```bash
# Enter the container
docker-compose exec toolbox bash

# Run from the mounted project directory (recommended for development)
cd /projects/fedora-dev-box
ansible-playbook setup-tmux.yml
ansible-playbook setup-packages.yml
ansible-playbook setup-all.yml

# Or run from the baked-in ansible directory
cd /usr/share/rhel-dev-toolbox/ansible
ansible-playbook playbooks/setup-tmux.yml
```

### One-liner from Host

Execute playbooks inside the container from your host:

```bash
# From the project root on your host
docker-compose exec toolbox ansible-playbook /projects/fedora-dev-box/setup-all.yml

# Or use the baked-in playbooks
docker-compose exec toolbox ansible-playbook /usr/share/rhel-dev-toolbox/ansible/playbooks/setup-tmux.yml
```

## Available Roles

### certificates

Installs custom CA certificates to the system trust store.

**Tags:** `all`, `certificates`

**What it does:**
- Installs CA certificates to `/etc/pki/ca-trust/source/anchors/`
- Updates system CA trust with `update-ca-trust extract`
- Default: Red Hat IT Root CA certificates (2015, 2022)

**Variables:**
- `ca_certificates` - Dictionary of certificates (embedded in secrets.yml)

### ldap

Configures LDAP, Kerberos, and SSH bastion for Red Hat infrastructure.

**Tags:** `all`, `ldap`

**What it does:**
- LDAP client configuration (`/etc/openldap/ldap.conf`)
- Kerberos IPA configuration (`/etc/krb5.conf.d/ipa_redhat_com`)
- SSH bastion configuration for dist-git
- LDAP-based SSH known hosts lookup

**Variables:**
- `ldap_uri`, `ldap_base`, `ldap_sasl_mech`, `ldap_sasl_nocanon`, `ldap_tls_reqcert`
- `distgit_bastion_host`

### config

Deploys RHEL Developer Toolbox system configuration files.

**Tags:** `all`, `config`

**What it deploys:**
- Profile script: `/etc/profile.d/rhel_dev_toolbox.sh`
- Utilities: `/usr/libexec/rhel-developer-toolbox/rdtx-check-config`
- Utilities: `/usr/libexec/rhel-developer-toolbox/rdtx_bind_mounts`

### tmux

Installs and configures tmux with developer-friendly defaults.

**Tags:** `all`, `tmux`

**Variables:**
- `tmux_user_config` (default: `true`) - Install config in user's home directory

**Features:**
- Mouse support
- Vim-style navigation
- Custom status bar
- 10,000 line scrollback
- Better split keybindings

### dnf-packages

Installs development packages using DNF.

**Tags:** `all`, `dnf`

**Variables:**
- `dnf_base_packages` - List of base packages (45+ packages by default)
- `dnf_extra_packages` - Additional packages to install
- `dnf_packages_to_remove` - Packages to remove (default: `p11-kit-server`)
- `dnf_install_weak_deps` - Install weak dependencies (default: `false`)
- `dnf_upgrade_all` - Upgrade all packages (default: `true`)
- `dnf_clean_all` - Clean DNF cache (default: `true`)

## Using Tags

Run specific roles using tags:

```bash
# Only run tmux configuration
ansible-playbook setup-all.yml --tags tmux

# Only run package installation
ansible-playbook setup-all.yml --tags dnf

# Run everything (default)
ansible-playbook setup-all.yml --tags all

# Skip specific roles
ansible-playbook setup-all.yml --skip-tags dnf
```

## Creating New Roles

```bash
cd ansible/roles
mkdir -p new-role/{tasks,files,templates,handlers,defaults,vars,meta}
```

Create `tasks/main.yml` with your tasks, then add the role to a playbook.
