#!/usr/bin/env python

import trustme

_CA_CERT_FILENAME = r'ca/acme-cert-authority.ca.public.pem'
_CA_PRIVATE_KEY_FILENAME = r'ca/acme-cert-authority.ca.private.pem'

ca = trustme.CA()
ca.cert_pem.write_to_path(_CA_CERT_FILENAME)
ca.private_key_pem.write_to_path(_CA_PRIVATE_KEY_FILENAME)
