import subprocess

valkey_client_path = "/home/valkeyuser/valkey/src/valkey-cli"
cert_path = "/home/valkeyuser/valkey/tests/tls/client-gamma.pem"
key_path = "/home/valkeyuser/valkey/tests/tls/client-gamma.private.pem"
cacert_path = "/home/valkeyuser/valkey/tests/tls/acme-cert-authority.ca.public.pem"
server_host = "server-alpha.network.local"
port = 6379

base_command = f"wsl {valkey_client_path} --tls --cert {cert_path} --key {key_path} --cacert {cacert_path} -h {server_host} -p {port}"

def run_command(command):
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        print(f"Error running command: {result.stderr.strip()}")
        return None

ping_command = f"{base_command} PING"
print(f"Ping Command: {ping_command}")
ping_result = run_command(ping_command)
print(f"Ping Result: {ping_result}")

get_memory_usage_command = f"{base_command} GET memory_usage"
print(f"Get Memory Usage Command: {get_memory_usage_command}")
memory_usage_result = run_command(get_memory_usage_command)
print(f"Memory Usage Result: {memory_usage_result}")
