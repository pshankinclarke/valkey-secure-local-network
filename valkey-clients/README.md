# Running Valkey Clients on Windows

This directory includes two scripts to run Valkey clients locally on Windows: one in PowerShell and one in Python. Follow the instructions below to use them.

## Setup

The setup is as follows:
- The Valkey server is running on `server-alpha`.
- A [monitoring script](../monitoring_script.sh) is running on `client-beta`.
- The client scripts in this directory are running on `client-gamma`, which is a Windows machine.

On the Windows machine (`client-gamma`), Valkey was installed through the Ubuntu app.

## PowerShell Script

### Edit the `valkey_client.ps1` Script:

Ensure the paths and server details match your setup:

```powershell
$valkeyClientPath = "/home/valkeyuser/valkey/src/valkey-cli"
$certPath = "/home/valkeyuser/valkey/tests/tls/client-gamma.pem"
$keyPath = "/home/valkeyuser/valkey/tests/tls/client-gamma.private.pem"
$cacertPath = "/home/valkeyuser/valkey/tests/tls/acme-cert-authority.ca.public.pem"
$serverHost = "server-alpha.network.local"
$port = 6379
```

### Run the PowerShell Script:

Use the provided batch file to run the PowerShell script:

```bat
@echo off
echo Running PowerShell script...
echo Script Path: "C:\Users\valkeyuser\valkey_clients\valkey_client.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\valkeyuser\valkey_clients\valkey_client.ps1"
pause
```

From the command prompt, run:

```plaintext
C:\Users\valkeyuser\valkey_clients>run_script.bat
```

## Python Script

### Edit the `valkey_client.py` Script:

Ensure the paths and server details match your setup:

```python
valkey_client_path = "/home/valkeyuser/valkey/src/valkey-cli"
cert_path = "/home/valkeyuser/valkey/tests/tls/client-gamma.pem"
key_path = "/home/valkeyuser/valkey/tests/tls/client-gamma.private.pem"
cacert_path = "/home/valkeyuser/valkey/tests/tls/acme-cert-authority.ca.public.pem"
server_host = "server-alpha.network.local"
port = 6379
```

### Run the Python Script:

From the command prompt or Anaconda prompt, run:

```plaintext
C:\Users\valkeyuser\valkey_clients>python valkey_client.py
```
