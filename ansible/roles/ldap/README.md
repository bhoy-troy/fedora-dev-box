# LDAP Role

Configures LDAP, Kerberos, and SSH bastion access for Red Hat internal infrastructure.

## Description

This role sets up authentication and access infrastructure for Red Hat internal systems:

1. **LDAP Configuration** (`/etc/openldap/ldap.conf`)
   - LDAP client configuration for IPA servers
   - SASL/GSSAPI authentication
   - TLS certificate validation

2. **Kerberos Configuration** (`/etc/krb5.conf.d/ipa_redhat_com`)
   - IPA Kerberos realm configuration
   - Required for GSSAPI authentication

3. **SSH Bastion Configuration** (`/etc/ssh/ssh_config.d/00-distgit-bastion.conf`)
   - Automatic ProxyJump through bastion for dist-git
   - Routes pkgs.devel.redhat.com and pkgs-stage.devel.redhat.com through bastion
   - GSSAPI authentication for SSH

4. **SSH Known Hosts Lookup** (`/usr/local/bin/known-hosts-rh-ldap`)
   - LDAP-based SSH known hosts lookup
   - Dynamically retrieves SSH keys from LDAP

## Tags

`all`, `ldap`

## Variables

### LDAP Configuration

#### `ldap_uri`
LDAP server URIs (space-separated list of ldaps:// URLs).  
Default: Red Hat internal IPA servers

#### `ldap_base`
LDAP base DN for searches.  
Default: `dc=ipa,dc=redhat,dc=com`

#### `ldap_sasl_mech`
SASL authentication mechanism.  
Default: `GSSAPI`

#### `ldap_sasl_nocanon`
SASL canonicalization setting.  
Default: `on`

#### `ldap_tls_reqcert`
TLS certificate verification level (`demand`, `allow`, `try`, `never`).  
Default: `demand`

#### `ldap_host`
LDAP server for SSH host key lookups (single ldap:// or ldaps:// URL).  
Default: `ldap://s2.idm-001.prod.rdu2.dc.redhat.com`

**Note:** This is used by the `known-hosts-rh-ldap` script to retrieve SSH host keys from IPA/LDAP.

### Kerberos Configuration

#### `kerberos_realm`
Kerberos realm for authentication.  
Default: `IPA.REDHAT.COM`

**Note:** This is the default realm used for GSSAPI authentication. Must match your organization's Kerberos setup.

### SSH Bastion Configuration

#### `distgit_bastion_host`
Bastion host for dist-git SSH access.  
Default: `bastion-iad2.corp.redhat.com`

This configures SSH to:
- Create a `distgit-bastion` host alias pointing to the bastion
- Route connections to `pkgs.devel.redhat.com` and `pkgs-stage.devel.redhat.com` through the bastion
- Use GSSAPI authentication
- Use LDAP-based known hosts lookup

## Files Deployed

| Source | Destination | Mode | Purpose |
|--------|-------------|------|---------|
| `ldap.conf.j2` | `/etc/openldap/ldap.conf` | 0644 | LDAP client configuration |
| `ipa_redhat_com.j2` | `/etc/krb5.conf.d/ipa_redhat_com` | 0644 | Kerberos IPA realm config |
| `00-distgit-bastion.conf.j2` | `/etc/ssh/ssh_config.d/00-distgit-bastion.conf` | 0444 | SSH bastion configuration |
| `known-hosts-rh-ldap.sh.j2` | `/usr/local/bin/known-hosts-rh-ldap` | 0755 | LDAP-based SSH known hosts |

## Example Playbook

### Basic Usage

```yaml
---
- name: Configure LDAP and authentication
  hosts: all
  roles:
    - role: ldap
```

### With Custom Configuration

```yaml
---
- name: Configure LDAP with custom settings
  hosts: all
  roles:
    - role: ldap
      ldap_uri: "ldaps://ldap1.example.com/"
      ldap_base: "dc=example,dc=com"
      distgit_bastion_host: "bastion.example.com"
```

### Using secrets.yml

**Recommended approach:**

```yaml
# secrets.yml
ldap_uri: "ldaps://s1.idm-001.prod.iad2.dc.redhat.com/ ..."
ldap_base: "dc=ipa,dc=redhat,dc=com"
ldap_sasl_mech: "GSSAPI"
ldap_sasl_nocanon: "on"
ldap_tls_reqcert: "demand"
ldap_host: "ldap://s2.idm-001.prod.rdu2.dc.redhat.com"
kerberos_realm: "IPA.REDHAT.COM"
distgit_bastion_host: "bastion-iad2.corp.redhat.com"
```

Run with:
```bash
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

## Dependencies

- **Kerberos client** must be installed (kinit, klist)
- **GSSAPI authentication** requires valid Kerberos ticket
- **VPN connection** to Red Hat network for bastion access

## Usage After Configuration

### Kerberos Authentication

```bash
# Obtain Kerberos ticket (using configured realm)
kinit username@IPA.REDHAT.COM

# Verify ticket
klist

# Test LDAP
ldapsearch -Y GSSAPI -H ldaps://s1.idm-001.prod.iad2.dc.redhat.com -b dc=ipa,dc=redhat,dc=com
```

**Note:** Replace `IPA.REDHAT.COM` with your configured `kerberos_realm` value.

### SSH Through Bastion

```bash
# Direct connection (automatically uses bastion)
ssh pkgs.devel.redhat.com

# Stage environment
ssh pkgs-stage.devel.redhat.com

# Connect to bastion directly
ssh distgit-bastion
```

### LDAP Known Hosts

The `known-hosts-rh-ldap` script is automatically called by SSH for configured hosts. No manual intervention needed.

## Notes

- All configuration requires connection to Red Hat internal network (VPN)
- GSSAPI authentication requires valid Kerberos credentials
- SSH bastion configuration uses ProxyJump for transparent routing
- LDAP client configuration supports multiple IPA servers for redundancy
