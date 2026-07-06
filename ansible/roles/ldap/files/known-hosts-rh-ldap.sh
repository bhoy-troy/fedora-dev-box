#!/bin/bash

# Find host keys from RH corporate LDAP
# These LDAP queries may take a while to complete, so we cache the results
# in a file in the /run hierarchy so that they are automatically expired
# when the host reboots This cache is shared with the host and any other
# toolbox containers.

if [[ -z "$1" ]]; then
    echo "Error: must specify host"
    echo "Usage: $0 <host>"
    exit 1
fi

LDAP_HOST=ldap://s2.idm-001.prod.rdu2.dc.redhat.com
export TARGET_HOST=$1

CACHE_DIR="/run/user/$(id -u)/ssh_host_cache"
CACHE_FILE="${CACHE_DIR}/${TARGET_HOST}"

mkdir -p "${CACHE_DIR}"

if [[ -f "${CACHE_FILE}" ]]; then
    cat "${CACHE_FILE}"
    exit 0
fi

LDAP_CN=$(dig -t CNAME ${TARGET_HOST} +short | sed -e 's/.$//')

LDAP_RESULT=$(ldapsearch -LLL -o ldif_wrap=no -Y GSSAPI -H ${LDAP_HOST} -b cn=computers,cn=accounts,dc=ipa,dc=redhat,dc=com "(cn=${LDAP_CN})" cn ipaSshPubKey 2>/dev/null)
if [[ -z ${LDAP_RESULT} ]]; then
    echo "Error: LDAP lookup for ${TARGET_HOST} failed"
    exit 1
fi

echo "${LDAP_RESULT}" | awk '/^ipaSshPubKey/ { $1=""; print ENVIRON["TARGET_HOST"] $0}' | sort | tee "${CACHE_FILE}"
