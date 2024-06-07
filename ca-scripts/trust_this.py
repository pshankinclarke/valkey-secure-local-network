#!/usr/bin/env python

_DEBUG_OUTPUT = True
_GENERATE_CERTS = True

_ORGANIZATION_NAME = 'Generic Organization'

import trustme

_CA_CERT_FILENAME = r'ca/generic-cert-authority.ca.public.pem'
_CA_PRIVATE_KEY_FILENAME = r'ca/generic-cert-authority.ca.private.pem'
_CERT_STORAGE_FOLDER = 'servers/'
_LOCAL_DOMAIN = 'network.local'

# Verify that the CA has been established and that the public and private keys exist

import os

_CA_FILENAMES = (_CA_CERT_FILENAME, _CA_PRIVATE_KEY_FILENAME)
_ca_path_exists = all(os.path.exists(filename) for filename in _CA_FILENAMES)
assert _ca_path_exists, f'An expected path was not found! ({_CA_FILENAMES})'

_ca_path_is_file = all(os.path.isfile(filename) for filename in _CA_FILENAMES)
assert _ca_path_is_file, 'Certificate authority files incorrectly stored!'

# Attempt to initialize `ca` from existing certificate authority files
try:
    with open(_CA_CERT_FILENAME, 'rb') as public_cert, open(_CA_PRIVATE_KEY_FILENAME, 'rb') as private_key:
        ca = trustme.CA.from_pem(public_cert.read(), private_key.read())
except:
    ca = None

assert ca, 'Failed to reinitialize existing certificate authority!'

# Identify hosts to trust

import sys
hosts_to_trust = {}

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        prepared_host = [host.strip() for host in arg.split(',')]
        hosts_to_trust[prepared_host[0]] = prepared_host
else:
    # -- Load hostnames from host_cache directory (if exists)
    _HOSTS_ON_DOMAIN_FILENAME = r'host_cache/hosts_on_domain.txt'
    _HOSTS_SPECIAL_FILENAME = r'host_cache/hosts_special.txt'
    _HOST_CACHE_FILENAMES = (_HOSTS_ON_DOMAIN_FILENAME, _HOSTS_SPECIAL_FILENAME)
    _host_cache_path_exists = all(os.path.exists(filename) for filename in _HOST_CACHE_FILENAMES)
    _host_cache_is_file = all(os.path.isfile(filename) for filename in _HOST_CACHE_FILENAMES)
    assert _host_cache_path_exists and _host_cache_is_file, 'No hosts to trust!'

    # -- Add hosts from host_cache
    try:
        # -- -- Add domain hosts
        _LOCAL_DOMAIN = 'network.local'

        with open(_HOSTS_ON_DOMAIN_FILENAME, 'r') as f:
            for line in f:
                prepared_host = [host.strip() for host in line.split(',')]
                # -- -- -- Conditionally add fully-qualified domain name (FQDN)
                if not any(hostname.lower().endswith(_LOCAL_DOMAIN.lower()) for hostname in prepared_host):
                    hostname = prepared_host[0]
                    FQDN = f'{hostname}.{_LOCAL_DOMAIN}'
                    prepared_host.append(FQDN)
                hosts_to_trust[prepared_host[0]] = prepared_host

        # -- -- Add 'special' or off-domain hosts
        with open(_HOSTS_SPECIAL_FILENAME, 'r') as f:
            for line in f:
                prepared_host = [host.strip() for host in line.split(',')]
                hosts_to_trust[prepared_host[0]] = prepared_host

    except:
        pass

# -- Main program action (certificate generation)
import ssl

if _GENERATE_CERTS:
    assert os.path.exists(_CERT_STORAGE_FOLDER), f'The `{_CERT_STORAGE_FOLDER}` must exist to store the new certificates!'
    client_ssl_context = ssl.create_default_context()
    ca.configure_trust(client_ssl_context)

hostnames = sorted(hosts_to_trust.keys())
for ndx in range(len(hostnames)):
    hostname = hostnames[ndx]
    identities = hosts_to_trust[hostname]
    if hostname.strip() and len(identities) > 0:
        if _DEBUG_OUTPUT:
            print(ndx, hostname, '->', identities)
        if _GENERATE_CERTS:
            cert = ca.issue_cert(*identities, organization_name=_ORGANIZATION_NAME)
            append = False
            for blob in cert.cert_chain_pems:
                blob.write_to_path(f'{_CERT_STORAGE_FOLDER}{hostname}.pem', append=append)
                append = True
            cert.private_key_pem.write_to_path(f'{_CERT_STORAGE_FOLDER}{hostname}.private.pem')
