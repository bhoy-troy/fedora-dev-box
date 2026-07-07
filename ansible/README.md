# Ansible Playbooks and Roles

This directory contains Ansible playbooks and roles for configuring the RHEL Developer Toolbox container.

## Quick Start

1. **Create secrets file:**
   ```bash
   cp secrets.yml.example secrets.yml
   nano secrets.yml  # Add your organization's values
   ```

2. **Encrypt with Ansible Vault:**
   ```bash
   ansible-vault encrypt secrets.yml
   echo "your-vault-password" > .vault_pass
   chmod 600 .vault_pass
   ```
   
   📖 **See [VAULT-GUIDE.md](VAULT-GUIDE.md) for complete vault documentation**

3. **Run playbooks:**
   ```bash
   # Inside container
   cd /projects/fedora-dev-box
   ansible-playbook setup-all.yml \
     --extra-vars @ansible/secrets.yml \
     --vault-password-file ansible/.vault_pass
   ```

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

### rcm-tools

Configures Red Hat Release Configuration Management Tools repository.

**Tags:** `all`, `rcm-tools`

**What it does:**
- Installs RCM GPG key (`/etc/pki/rpm-gpg/RPM-GPG-KEY-rcminternal`)
- Deploys RCM Tools repository configuration
- Uses HTTPS to Red Hat internal infrastructure

**Variables:**
- `rcm_tools_enabled` (default: `true`)

### copr-repos

Enables COPR repositories for development tools.

**Tags:** `all`, `copr-repos`

**What it does:**
- Enables 7 COPR repositories using `dnf copr enable`
- Internal Red Hat COPR (VPN required): @osh/osh-prod, lpol/qa-tools, etc.
- Public COPR: sgallagh/dev-toolbox-extras

**Variables:**
- `copr_repositories` - List of COPR repos to enable

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

## Managing Secrets with Ansible Vault

All sensitive configuration values (LDAP URIs, certificates, GPG keys, repository URLs) are stored in `secrets.yml` and should be encrypted with Ansible Vault.

### Initial Setup

**1. Copy the example secrets file:**

```bash
cd ansible
cp secrets.yml.example secrets.yml
```

**2. Edit with your organization's values:**

```bash
# Edit the file with your actual secrets
nano secrets.yml

# Update:
# - LDAP URIs and base DN
# - Kerberos realm
# - Bastion host
# - COPR repositories
# - RCM Tools URL and GPG key
# - CA certificates
```

**3. Encrypt the secrets file:**

```bash
# Encrypt secrets.yml (will prompt for password)
ansible-vault encrypt secrets.yml

# You'll be prompted to enter and confirm a vault password
New Vault password: 
Confirm New Vault password: 
Encryption successful
```

**4. Create a vault password file (recommended for development):**

```bash
# Store vault password in a file (NEVER commit this!)
echo "your-vault-password" > .vault_pass

# Ensure it's in .gitignore
echo ".vault_pass" >> ../.gitignore

# Secure the file
chmod 600 .vault_pass
```

### Working with Encrypted Secrets

**View encrypted file:**

```bash
# View contents without decrypting the file
ansible-vault view secrets.yml

# With password file
ansible-vault view secrets.yml --vault-password-file .vault_pass
```

**Edit encrypted file:**

```bash
# Edit encrypted file (opens in $EDITOR)
ansible-vault edit secrets.yml

# With password file
ansible-vault edit secrets.yml --vault-password-file .vault_pass
```

**Decrypt file temporarily:**

```bash
# Decrypt (use with caution)
ansible-vault decrypt secrets.yml

# Make changes
nano secrets.yml

# Re-encrypt
ansible-vault encrypt secrets.yml
```

**Change vault password:**

```bash
# Change the password
ansible-vault rekey secrets.yml

# Or with password file
ansible-vault rekey secrets.yml --vault-password-file .vault_pass
```

### Running Playbooks with Vault

**With password prompt:**

```bash
# Will prompt for vault password
ansible-playbook setup-all.yml --extra-vars @secrets.yml --ask-vault-pass
```

**With password file:**

```bash
# Use vault password file
ansible-playbook setup-all.yml --extra-vars @secrets.yml --vault-password-file .vault_pass

# From project root (recommended)
cd /projects/fedora-dev-box
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml --vault-password-file ansible/.vault_pass
```

**With environment variable:**

```bash
# Set vault password in environment
export ANSIBLE_VAULT_PASSWORD_FILE=ansible/.vault_pass

# Run playbook (will automatically use password file)
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

### Encrypting Specific Strings

Instead of encrypting the entire file, you can encrypt individual values:

```bash
# Encrypt a single value
ansible-vault encrypt_string 'secret-value' --name 'variable_name'

# Example: Encrypt a password
ansible-vault encrypt_string 'MySecretPassword123' --name 'some_password'

# Output can be pasted into YAML:
ldap_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653238336464626566653063...
```

### Best Practices

**Security:**
- ✅ Always encrypt `secrets.yml` before committing to git
- ✅ Store vault password file (`.vault_pass`) outside the repository or in `.gitignore`
- ✅ Use different vault passwords for different environments (dev/staging/prod)
- ❌ Never commit unencrypted secrets
- ❌ Never commit vault password files
- ❌ Never share vault passwords via insecure channels

**Development workflow:**

```bash
# 1. Start with example
cp secrets.yml.example secrets.yml

# 2. Add your secrets
nano secrets.yml

# 3. Encrypt immediately
ansible-vault encrypt secrets.yml

# 4. Create password file for convenience
echo "dev-password" > .vault_pass
chmod 600 .vault_pass

# 5. Edit when needed
ansible-vault edit secrets.yml --vault-password-file .vault_pass

# 6. Run playbooks
ansible-playbook setup-all.yml --extra-vars @secrets.yml --vault-password-file .vault_pass
```

**Team workflow:**

```bash
# Share vault password securely (e.g., password manager, encrypted communication)
# Each developer stores it in their own .vault_pass (not committed)

# Developer 1
echo "team-vault-password" > .vault_pass

# Developer 2  
echo "team-vault-password" > .vault_pass

# Both can now edit secrets
ansible-vault edit secrets.yml --vault-password-file .vault_pass
```

### Vault Password Storage Options

**Option 1: Password file (development)**
```bash
echo "password" > .vault_pass
chmod 600 .vault_pass
```

**Option 2: Script (for integration)**
```bash
#!/bin/bash
# get-vault-pass.sh
# Could fetch from password manager, AWS Secrets Manager, etc.
echo "your-password"
```

```bash
chmod +x get-vault-pass.sh
ansible-playbook setup-all.yml --vault-password-file ./get-vault-pass.sh
```

**Option 3: Environment variable**
```bash
export ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass
ansible-playbook setup-all.yml --extra-vars @secrets.yml
```

**Option 4: Prompt each time (most secure)**
```bash
ansible-playbook setup-all.yml --extra-vars @secrets.yml --ask-vault-pass
```

### Checking Vault Status

```bash
# Check if file is encrypted
head -n 1 secrets.yml
# If encrypted, shows: $ANSIBLE_VAULT;1.1;AES256
# If not encrypted, shows: ---

# List encrypted files
find . -type f -exec grep -l '$ANSIBLE_VAULT' {} \;
```

### Troubleshooting

**Wrong password:**
```
ERROR! Decryption failed (no vault secrets were found that could decrypt)
```
Solution: Use correct vault password

**File not encrypted:**
```bash
# If you forgot to encrypt
ansible-vault encrypt secrets.yml
```

**Can't edit file:**
```bash
# Make sure you have EDITOR set
export EDITOR=nano  # or vim, emacs, etc.
ansible-vault edit secrets.yml
```

**Multiple vault passwords:**

If you have multiple vaults with different passwords, use vault IDs:

```bash
# Encrypt with vault ID
ansible-vault encrypt --vault-id dev@prompt secrets.yml

# Run with vault ID
ansible-playbook setup-all.yml --vault-id dev@.vault_pass
```

## Creating New Roles

```bash
cd ansible/roles
mkdir -p new-role/{tasks,files,templates,handlers,defaults,vars,meta}
```

Create `tasks/main.yml` with your tasks, then add the role to a playbook.
