# Fedora Dev Box

Containerized Fedora development environment with Ansible-based configuration management.

## Quick Start


### __NOTE__ the VPM needs to be on
```bash
# Build, start, and configure
docker-compose build
docker-compose up -d
docker-compose exec toolbox bash

# Inside container: Run Ansible to configure environment
cd /projects/fedora-dev-box
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass 
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

##### There are multiple ways to use the vault password 

__Ask for it to be input__

    ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml --ask-vault-pass

__set env var__

    ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml

__Add  `vault_password_file` to .ansible.cfg__

    [defaults]
    roles_path = ./ansible/roles
    inventory = ./ansible/inventory
    vault_password_file = .vault_pass


## What This Provides

- **Fedora Toolbox** with 45+  Fedora development packages pre-installed
- **Ansible roles** for environment configuration (tmux, packages, etc.)
- **Host Podman integration** via shared socket
- **Red Hat internal configs** (certificates, Kerberos, LDAP, COPR repos)

 
## Key Features

✅ Pre-configured with Red Hat internal tools and certificates  
✅ Ansible-based configuration (modify and re-run without rebuilding)  
✅ Host Podman socket shared (no nested containers)  
✅ Project directory mounted at `/projects`  
✅ 45+ packages: fedpkg, rhpkg, beaker, tmt, koji, podman-remote, etc.

## Requirements

- Docker/Podman with docker-compose
- **VPN to Corporate internal network** (required during build)
- macOS or Linux host

## License

See [LICENCE.md](LICENCE.md)
