# Certificate Authority (CA) Scripts

The certificates generated are for testing purposes only and should never be used in any real or production environment.

## How to Use the Scripts

1. **Generate CA:**
   Run `generate_ca.py` to create the CA certificate and private key.
   ```bash
   python generate_ca.py
   ```

2. **Generate Certificates for Hosts:**
   Run `trust_this.py` to generate certificates for your hosts.
   ```bash
   python trust_this.py [hostname1,hostname2,...]
   ```
   If no hostnames are provided as arguments, the script will attempt to load hostnames from `host_cache/hosts_on_domain.txt` and `host_cache/hosts_special.txt`.
