# Ansible Vault Cheat Sheet

## Setup (One-time)

```bash
# 1. Create secrets
cp secrets.yml.example secrets.yml
nano secrets.yml

# 2. Encrypt
ansible-vault encrypt secrets.yml

# 3. Save password
echo "your-password" > .vault_pass
chmod 600 .vault_pass
```

## Common Commands

```bash
# View
ansible-vault view secrets.yml --vault-password-file .vault_pass

# Edit
ansible-vault edit secrets.yml --vault-password-file .vault_pass

# Encrypt
ansible-vault encrypt secrets.yml

# Decrypt
ansible-vault decrypt secrets.yml

# Change password
ansible-vault rekey secrets.yml

# Check if encrypted
head -n 1 secrets.yml  # Shows: $ANSIBLE_VAULT;1.1;AES256
```

## Run Playbooks

```bash
# With password file
ansible-playbook setup-all.yml \
  --extra-vars @ansible/secrets.yml \
  --vault-password-file ansible/.vault_pass

# With password prompt
ansible-playbook setup-all.yml \
  --extra-vars @ansible/secrets.yml \
  --ask-vault-pass

# With environment variable
export ANSIBLE_VAULT_PASSWORD_FILE=ansible/.vault_pass
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

## Inside Container

```bash
# Set password location
export ANSIBLE_VAULT_PASSWORD_FILE=/projects/fedora-dev-box/ansible/.vault_pass

# Run from project root
cd /projects/fedora-dev-box
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

## Security Reminders

✅ **DO:**
- Encrypt secrets.yml before committing
- Keep .vault_pass in .gitignore
- Use strong passwords
- Share password securely (password manager)

❌ **DON'T:**
- Commit unencrypted secrets
- Commit .vault_pass file
- Share password via chat/email
- Use weak passwords

## Troubleshooting

**Wrong password:**
```
ERROR! Decryption failed
```
→ Use correct password

**Not encrypted:**
```bash
ansible-vault encrypt secrets.yml
```

**Can't edit:**
```bash
export EDITOR=nano
ansible-vault edit secrets.yml
```

---

📖 Full guide: [VAULT-GUIDE.md](VAULT-GUIDE.md)
