import subprocess
import os

valkey_client_path = "/home/valkeyuser/valkey/src/valkey-cli"
cert_path = "/home/valkeyuser/valkey/tests/tls/client-gamma.pem"
key_path = "/home/valkeyuser/valkey/tests/tls/client-gamma.private.pem"
cacert_path = "/home/valkeyuser/valkey/tests/tls/acme-cert-authority.ca.public.pem"
server_host = "server-alpha.network.local"
port = 6379

username = os.getenv("VALKEY_USERNAME")
password = os.getenv("VALKEY_PASSWORD")

base_command = [
    "wsl",
    valkey_client_path,
    "--tls",
    "--cert", cert_path,
    "--key", key_path,
    "--cacert", cacert_path,
    "--user", username,
    "-h", server_host,
    "-p", str(port),
    "-a", password
]

def run_command(command):
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=10)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr.strip()}")
        return f"Error: {e.stderr.strip()}"
    except subprocess.TimeoutExpired as e:
        print(f"Command timed out: {e}")
        return "Error: Command timed out"

ping_command = base_command + ["PING"]
print("Ping Command:", " ".join(ping_command))
ping_result = run_command(ping_command)
print("Ping Result:", ping_result)

get_memory_usage_command = base_command + ["GET", "memory_usage"]
print("Get Memory Usage Command:", " ".join(get_memory_usage_command))
memory_usage_result = run_command(get_memory_usage_command)
print("Memory Usage Result:", memory_usage_result)
