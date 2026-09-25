# Ansible Vault Quick Reference Guide

## Quick Start

### 1. Create and encrypt secrets

```bash
# Copy example
cp secrets.yml.example secrets.yml

# Edit with your values
nano secrets.yml

# Encrypt
ansible-vault encrypt secrets.yml
```

### 2. Create vault password file (optional)

```bash
# Create password file
echo "your-password" > .vault_pass
chmod 600 .vault_pass

# Add to .gitignore (if not already)
echo ".vault_pass" >> ../.gitignore
```

### 3. Run playbooks

```bash
# With password prompt
ansible-playbook setup-all.yml --extra-vars @secrets.yml --ask-vault-pass

# With password file
ansible-playbook setup-all.yml --extra-vars @secrets.yml --vault-password-file .vault_pass

# From project root
cd /projects/fedora-dev-box
ansible-playbook setup-all.yml \
  --extra-vars @ansible/secrets.yml \
  --vault-password-file ansible/.vault_pass
```

## Common Commands

### Create/Encrypt

```bash
# Encrypt existing file
ansible-vault encrypt secrets.yml

# Create new encrypted file
ansible-vault create new-secrets.yml

# Encrypt a string value
ansible-vault encrypt_string 'secret-value' --name 'variable_name'
```

### View/Edit

```bash
# View encrypted file
ansible-vault view secrets.yml

# Edit encrypted file
ansible-vault edit secrets.yml

# With password file
ansible-vault edit secrets.yml --vault-password-file .vault_pass
```

### Decrypt/Rekey

```bash
# Decrypt file (use with caution!)
ansible-vault decrypt secrets.yml

# Change vault password
ansible-vault rekey secrets.yml

# Verify encryption
head -n 1 secrets.yml
# Should show: $ANSIBLE_VAULT;1.1;AES256
```

## Password Management

### Method 1: Interactive (most secure)

```bash
ansible-playbook setup-all.yml --extra-vars @secrets.yml --ask-vault-pass
```

### Method 2: Password file (convenience)

```bash
echo "password" > .vault_pass
chmod 600 .vault_pass

ansible-playbook setup-all.yml --extra-vars @secrets.yml --vault-password-file .vault_pass
```

### Method 3: Environment variable

```bash
export ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass

ansible-playbook setup-all.yml --extra-vars @secrets.yml
```

### Method 4: Script (integration)

```bash
#!/bin/bash
# get-vault-pass.sh
# Fetch from password manager, AWS Secrets Manager, etc.
echo "your-password"
```

```bash
chmod +x get-vault-pass.sh
ansible-playbook setup-all.yml --vault-password-file ./get-vault-pass.sh
```

## Workflow Examples

### First-time setup

```bash
# 1. Copy and customize secrets
cp secrets.yml.example secrets.yml
nano secrets.yml

# 2. Encrypt
ansible-vault encrypt secrets.yml
# Enter password when prompted

# 3. Save password for later (optional)
echo "your-password" > .vault_pass
chmod 600 .vault_pass

# 4. Test
ansible-vault view secrets.yml --vault-password-file .vault_pass
```

### Daily editing

```bash
# Edit secrets
ansible-vault edit secrets.yml --vault-password-file .vault_pass

# Run playbook
ansible-playbook setup-all.yml \
  --extra-vars @secrets.yml \
  --vault-password-file .vault_pass
```

### Inside container

```bash
# From host: enter container with vault password
docker-compose exec toolbox bash

# Inside container: set password
export ANSIBLE_VAULT_PASSWORD_FILE=/projects/fedora-dev-box/ansible/.vault_pass

# Run playbook
cd /projects/fedora-dev-box
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

## What to Encrypt

In `secrets.yml`, encrypt all sensitive values:

✅ **Always encrypt:**
- LDAP URIs and credentials
- Kerberos realm information
- Internal hostnames and bastion hosts
- GPG keys
- CA certificates
- Repository URLs (if internal)
- Any credentials or tokens

❌ **Don't need to encrypt:**
- Public COPR repository names
- Package lists
- Boolean flags and defaults
- Public URLs

## Security Best Practices

### DO:
- ✅ Encrypt secrets.yml before first commit
- ✅ Store .vault_pass in .gitignore
- ✅ Use strong, unique vault passwords
- ✅ Share vault password via secure channel (password manager, encrypted email)
- ✅ Use different passwords for dev/staging/production
- ✅ Regularly rotate vault passwords (ansible-vault rekey)

### DON'T:
- ❌ Commit unencrypted secrets
- ❌ Commit .vault_pass file
- ❌ Share vault password via Slack/email/chat
- ❌ Use weak or default passwords
- ❌ Reuse passwords across environments

## Troubleshooting

### Error: Decryption failed

```
ERROR! Decryption failed (no vault secrets were found that could decrypt)
```

**Solution:** Wrong password. Check:
```bash
# Verify file is encrypted
head -n 1 secrets.yml

# Try different password
ansible-vault view secrets.yml --ask-vault-pass
```

### Error: File not encrypted

If playbook requires encrypted file but you have plaintext:

```bash
# Encrypt the file
ansible-vault encrypt secrets.yml
```

### Can't edit file

```bash
# Make sure EDITOR is set
export EDITOR=nano  # or vim, emacs, code --wait

# Try again
ansible-vault edit secrets.yml
```

### Forgot vault password

Unfortunately, there's no way to recover the password. You'll need to:

```bash
# 1. Start fresh with unencrypted copy (if you have one)
cp secrets.yml.example secrets.yml

# 2. Fill in values again
nano secrets.yml

# 3. Encrypt with new password
ansible-vault encrypt secrets.yml
```

**Prevention:** Store vault password in a password manager!

### Check encryption status

```bash
# Is file encrypted?
head -n 1 secrets.yml

# Encrypted shows:
$ANSIBLE_VAULT;1.1;AES256

# Unencrypted shows:
---

# Find all encrypted files
find . -type f -exec grep -l '$ANSIBLE_VAULT' {} \;
```

## Advanced Usage

### Multiple vault passwords

Use vault IDs for different environments:

```bash
# Encrypt with ID
ansible-vault encrypt --vault-id dev@prompt secrets-dev.yml
ansible-vault encrypt --vault-id prod@prompt secrets-prod.yml

# Use with ID
ansible-playbook setup.yml --vault-id dev@.vault_pass_dev
```

### Encrypt only specific values

Instead of encrypting the whole file:

```bash
# Encrypt a single value
ansible-vault encrypt_string 'my-secret' --name 'secret_var'

# Paste output into YAML:
secret_var: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          363738...
```

### Convert encrypted file to string format

```bash
# Decrypt file
ansible-vault decrypt secrets.yml

# Encrypt specific values
ansible-vault encrypt_string "$(cat gpg-key.asc)" --name 'gpg_key'

# Paste into YAML file
```

## Quick Reference Table

| Task | Command |
|------|---------|
| Encrypt file | `ansible-vault encrypt secrets.yml` |
| Decrypt file | `ansible-vault decrypt secrets.yml` |
| View encrypted | `ansible-vault view secrets.yml` |
| Edit encrypted | `ansible-vault edit secrets.yml` |
| Change password | `ansible-vault rekey secrets.yml` |
| Encrypt string | `ansible-vault encrypt_string 'value' --name 'var'` |
| Run playbook | `ansible-playbook play.yml --ask-vault-pass` |
| With password file | `ansible-playbook play.yml --vault-password-file .vault_pass` |
| Check if encrypted | `head -n 1 secrets.yml` |

## Example: Complete Workflow

```bash
# Start fresh
cd /projects/fedora-dev-box/ansible

# Copy example
cp secrets.yml.example secrets.yml

# Customize
nano secrets.yml
# Update LDAP URIs, certificates, GPG keys, etc.

# Encrypt
ansible-vault encrypt secrets.yml
# Enter: MySecureVaultPassword123

# Save password
echo "MySecureVaultPassword123" > .vault_pass
chmod 600 .vault_pass

# Verify
ansible-vault view secrets.yml --vault-password-file .vault_pass

# Test playbook
cd /projects/fedora-dev-box
ansible-playbook setup-all.yml \
  --extra-vars @ansible/secrets.yml \
  --vault-password-file ansible/.vault_pass

# Later: edit secrets
ansible-vault edit ansible/secrets.yml \
  --vault-password-file ansible/.vault_pass

# Commit encrypted file (safe!)
git add ansible/secrets.yml
git commit -m "Add encrypted secrets"

# .vault_pass is NOT committed (in .gitignore)
```

## Resources

- [Ansible Vault Documentation](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
- [Best Practices for Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#variables-and-vaults)
