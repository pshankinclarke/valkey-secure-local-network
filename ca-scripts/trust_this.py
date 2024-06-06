#!/usr/bin/env python

import os
import sys
import ssl
import trustme

_DEBUG_OUTPUT = True
_GENERATE_CERTS = True
_ORGANIZATION_NAME = 'Acme Corporation'

_CA_CERT_FILENAME = r'ca/acme-cert-authority.ca.public.pem'
_CA_PRIVATE_KEY_FILENAME = r'ca/acme-cert-authority.ca.private.pem'
_CERT_STORAGE_FOLDER = 'servers/'
_LOCAL_DOMAIN = 'network.local'

# Verify that the CA has been established and that the public and private keys exist
_CA_FILENAMES =
