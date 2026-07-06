# DNF Packages Role

Installs development packages using DNF for RHEL/Fedora systems.

This role mirrors the package installation logic from the Dockerfile:
1. Installs DNF5 plugins first (dnf5-plugins, libdnf5-plugin-actions)
2. Installs base development packages with weak dependencies disabled
3. Installs any extra packages
4. Removes unwanted packages (p11-kit-server)
5. Upgrades all packages
6. Cleans DNF cache

## Variables

### `dnf_base_packages`
List of base development packages to install. Default includes 46 packages:
- Ansible (ansible)
- RHEL/Fedora packager tools (fedora-packager, rhel-packager, etc.)
- Build tools (argbash, bison, flex, rpmdevtools)
- Testing tools (beaker-client, tmt-all)
- Container tools (podman-remote, skopeo)
- Virtualization tools (libvirt-client, virt-manager)
- Development utilities (git-subtree, glab, jq, vim, nano, zsh)

### `dnf_extra_packages`
Additional packages to install beyond the base set. Default: `[]`

Example:
```yaml
dnf_extra_packages:
  - golang
  - rust
  - nodejs
```

### `dnf_packages_to_remove`
Packages to remove. Default: `[p11-kit-server]`

### `dnf_install_weak_deps`
Whether to install weak dependencies. Default: `false`

### `dnf_upgrade_all`
Upgrade all packages after installation. Default: `true`

### `dnf_clean_all`
Clean DNF cache after operations. Default: `true`

## Example Playbook

```yaml
---
- name: Install development packages
  hosts: all
  roles:
    - role: dnf-packages
      dnf_extra_packages:
        - golang
        - rust
```

## Minimal Installation

To skip base packages and only install specific packages:

```yaml
---
- name: Install minimal packages
  hosts: all
  roles:
    - role: dnf-packages
      dnf_base_packages: []
      dnf_extra_packages:
        - vim
        - git
        - tmux
      dnf_upgrade_all: false
```
