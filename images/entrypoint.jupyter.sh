#!/bin/sh
set -eu

# Configure environment via Ansible (same pattern as worker)
if [ -f /projects/fedora-dev-box/setup-all.yml ]; then
  cd /projects/fedora-dev-box
  ansible-playbook setup-all.yml --extra-vars @ansible/secrets.yml || echo "WARNING: Ansible provisioning failed"
fi

JUPYTER_TOKEN="${JUPYTER_TOKEN:-dev-notebook-token}"

mkdir -p ~/.jupyter

cat > ~/.jupyter/jupyter_server_config.py << CONF
c.PasswordIdentityProvider.token = "${JUPYTER_TOKEN}"
c.ServerApp.allow_remote_access = True
c.ServerApp.disable_check_xsrf = True
CONF

exec  jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --ServerApp.allow_root=True \
    --PasswordIdentityProvider.token="${JUPYTER_TOKEN}"
