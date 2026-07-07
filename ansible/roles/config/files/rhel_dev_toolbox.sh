if [ -r /run/.containerenv ]; then
  # Do this in a subshell so we don't leak the other variables here
  (
    . /run/.containerenv
    sudo hostname ${name}

    # Add bind mounts early, so if it replaces any config files, they will be
    # available for this script as well.

    # Check for bind mounts in order of precedence: shipped-with-RDTx, user
    # global, per-container. Later ones will override earlier ones.
    for cfg in \
      /usr/share/rhel-dev-toolbox/bind_mounts.yaml \
      "$HOME/.config/rhel-developer-toolbox/config/bind_mounts.yaml" \
      "$HOME/.config/rhel-developer-toolbox/config/${name}/bind_mounts.yaml"
    do
      if [ -r "$cfg" ]; then
        sudo /usr/libexec/rhel-developer-toolbox/rdtx_bind_mounts "$cfg"
      fi
    done

    # Note: Removed rdtx-apply-config autoconfigure
    # Use Ansible playbooks directly: ansible-playbook /projects/fedora-dev-box/setup-all.yml
  )
fi

if [ -r /run/.toolboxenv ]; then
  # We're running in a container started by toolbx
  # Ensure that we're using the default kerberos configuration by deleting
  # the special override for the credential cache location if it exists.
  rm -f /etc/krb5.conf.d/rdtx_ccache_override

  alias podman="podman-remote"
  alias rpm-ostree="flatpak-spawn --host rpm-ostree"
  alias flatpak="flatpak-spawn --host flatpak"

  if flatpak-spawn --host flatpak list --app --columns=application | grep -q com.visualstudio.code ; then
    mkdir -p $HOME/.local/lib $HOME/.local/bin
    if [ ! -x $HOME/.local/lib/toolbox-vscode/code.sh ]; then
      oldpwd=$(pwd)
      cd $HOME/.local/lib
      git clone https://github.com/owtaylor/toolbox-vscode.git &> /dev/null
      cd $oldpwd
    else
      oldpwd=$(pwd)
      cd $HOME/.local/lib/toolbox-vscode
      git pull &> /dev/null
      cd $oldpwd
    fi

    ln -sf $HOME/.local/lib/toolbox-vscode/code.sh $HOME/.local/bin/code
  fi
elif [ -r /run/.containerenv ]; then
  # We're running in a non-toolbox container (such as on Podman for Mac)
  # We need to modify the Kerberos environment to use a local DIR: cache
  # (which supports multiple credential types) instead of the default that
  # relies on the kernel keyring which is unavailable to us.
  cat << EOF > /etc/krb5.conf.d/rdtx_ccache_override
[libdefaults]
default_ccache_name = DIR:/var/tmp/krb5cc_%{uid}
EOF
fi
