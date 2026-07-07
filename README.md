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
ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml
```

## What This Provides

- **Fedora Toolbox** with 45+  Fedora development packages pre-installed
- **Ansible roles** for environment configuration (tmux, packages, etc.)
- **Host Podman integration** via shared socket
- **Red Hat internal configs** (certificates, Kerberos, LDAP, COPR repos)

## Ansible Playbooks (Run Inside Container)

```bash
# Complete setup (recommended)
ansible-playbook setup-all.yml

# Individual components
ansible-playbook setup-tmux.yml        # Tmux configuration
ansible-playbook setup-packages.yml    # Development packages
```

 
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
