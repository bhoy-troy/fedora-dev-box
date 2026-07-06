# Certificates Role

Installs custom CA certificates to the system trust store.

## Description

This role:
1. Copies CA certificate files to `/etc/pki/ca-trust/source/anchors/`
2. Updates the system CA trust store with `update-ca-trust extract`

Certificate files are stored in `ansible/secrets/certificates/` and are typically organization-specific root CA certificates.

## Tags

`all`, `certificates`

## Variables

### `ca_certificates`

Dictionary of CA certificates to install, with filename as key and certificate content as value.

**RECOMMENDED:** Define this in `secrets.yml` for centralized secret management.

**Default:** `{}` (empty, no certificates)

**In secrets.yml (recommended):**
```yaml
# secrets.yml
ca_certificates:
  2022-IT-Root-CA.pem: |
    -----BEGIN CERTIFICATE-----
    MIIGcjCCBFqgAwIBAgIFICIEEFwwDQYJKoZIhvcNAQEMBQAwgaMxCzAJBgNVBAYT
    ...
    -----END CERTIFICATE-----
  
  2015-IT-Root-CA.pem: |
    -----BEGIN CERTIFICATE-----
    MIIENDCCAxygAwIBAgIJANunI0D662cnMA0GCSqGSIb3DQEBCwUAMIGlMQswCQYD
    ...
    -----END CERTIFICATE-----
  
  my-company-ca.pem: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
```

**No certificates:**
```yaml
ca_certificates: {}
```

## Certificate Storage

**Certificates are stored directly in `secrets.yml`** as inline content, not as separate files.

**Benefits:**
- ✅ Single file to manage and encrypt
- ✅ Easy to use Ansible Vault
- ✅ No separate certificate files to track
- ✅ Certificates are automatically version controlled (when encrypted)

**Security:**
- Encrypt `secrets.yml` with Ansible Vault to protect certificate content
- The example file (`secrets.yml.example`) can be committed to show the format
- Never commit unencrypted `secrets.yml` with real certificates

## Handlers

### `Update CA trust`
Runs `update-ca-trust extract` to update the system CA trust store after installing certificates.

## Example Playbook

### Basic Usage (uses default certificates)

```yaml
---
- name: Install CA certificates
  hosts: all
  roles:
    - role: certificates
```

### Custom Certificates

```yaml
---
- name: Install custom CA certificates
  hosts: all
  roles:
    - role: certificates
      ca_certificates:
        - /tmp/my-company-root-ca.pem
        - /tmp/my-company-intermediate-ca.pem
```

### Skip Certificate Installation

```yaml
---
- name: Setup without certificates
  hosts: all
  roles:
    - role: certificates
      ca_certificates: []
```

### Using with secrets.yml

**Recommended approach:**

1. Copy the example secrets file:
```bash
cd ansible
cp secrets.yml.example secrets.yml
```

2. The example already contains Red Hat IT Root CA certificates. Add your custom certificates:
```yaml
# secrets.yml
ca_certificates:
  2022-IT-Root-CA.pem: |
    -----BEGIN CERTIFICATE-----
    ...existing content...
    -----END CERTIFICATE-----
  
  my-custom-ca.pem: |
    -----BEGIN CERTIFICATE-----
    ...your certificate content...
    -----END CERTIFICATE-----
```

3. Encrypt with Ansible Vault (recommended):
```bash
ansible-vault encrypt secrets.yml
```

4. Run playbook with secrets:
```bash
# Without encryption (not recommended for production)
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml

# With Ansible Vault encryption (recommended)
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml --ask-vault-pass
```

### Using with setup-all.yml

The certificates role runs before other configuration to ensure SSL/TLS connections work:

```bash
# Install all certificates (using defaults or secrets.yml)
ansible-playbook setup-all.yml --extra-vars @secrets.yml

# Skip certificates
ansible-playbook setup-all.yml --skip-tags certificates
```

## Dependencies

None

## Notes

- Certificates must be in PEM format
- The system CA trust store is updated immediately after installation
- Handlers ensure `update-ca-trust` runs only once even if multiple certificates are installed
- The role uses `become: true` to run with elevated privileges
