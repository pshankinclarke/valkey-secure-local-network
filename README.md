# Valkey Secure Client-Server Communication on Local Network

Hello! Thank you for stopping by. Here you'll find tools for managing and interacting with Valkey across different machines on a local network.

**A necessary proviso:** this guide is not exhaustive, definitive, or necessarily novel. Its primary purpose stems from a personal motivation to better catalog and make sense of the collection of files, sticky notes, and documents that I've accumulated while using Valkey. Throughout this guide, I've aimed to reference more reliable sources, particularly [Valkey](https://github.com/valkey-io/valkey/tree/unstable) itself.

## Running Valkey Clients on Windows

If you're interested in running Valkey clients locally on Windows with Python or PowerShell, you can find more information [here](valkey-clients).

## Getting Started

### Prerequisites

To begin, ensure that Valkey is cloned, built, tested, and running with TLS. More detailed instructions can be found [here](https://github.com/valkey-io/valkey/blob/unstable/TLS.md). The following packages might be useful:

```sh
sudo apt-get install expect libssl-dev pkg-config gcc g++ make openssl build-essential
```

If you run into issues during the `make` process, you can use the following command before retrying:

```sh
make distclean
```

### Configuring Certificate Authority (CA)

To configure a Certificate Authority (CA) and create certificates and keys for the server and clients, you can use [trustme](https://trustme.readthedocs.io/en/latest/) to easily generate TLS certificates.

The provided [scripts](ca-scripts) are based on `trustme`. Technically, these are real certificates, but they are signed by your CA, which is not trusted by anyone else. You can trust it for your tests, but do not use it for anything real.

#### Testing Certificate Authority

Verify the CA setup using OpenSSL commands:

```sh
# Verify the server certificate
openssl x509 -in ./tests/tls/server-alpha.pem -text -noout

# Check the server private key
openssl pkey -in ./tests/tls/server-alpha.private.pem -check

# Verify the CA certificate
openssl x509 -in ./tests/tls/acme-cert-authority.ca.public.pem -text -noout
```

### Update the Configuration File

Once Valkey is built and tested on the machine designated to run your server process, you can proceed to edit the configuration file. For the purposes of this guide, we will refer to this machine as `server-alpha`.

1. **Edit the Configuration File:**

Open the `valkey.conf` (or `redis.conf`) file on `server-alpha`:

```bash
sudo nano /path/to/valkey.conf
```

2. **Update the Bind Directive:**

Change the bind directive to listen on all network interfaces. Replace:

```plaintext
bind 127.0.0.1 -::1
```

with:

```plaintext
bind 0.0.0.0
```

**Explanation:**

- `127.0.0.1` is the loopback Internet protocol (IP) address, also referred to as the “localhost.” It is used to establish an IP connection to the same machine being used by the end-user.
- `::1` is the IPv6 equivalent of `127.0.0.1`.
- `0.0.0.0` is a non-routable meta-address used to designate an invalid, unknown, or non-applicable target (a no particular address placeholder). In this context, it allows the server to listen on all available network interfaces to communicate with clients across different machines.

3. **Protected Mode Configuration**

Protected mode restricts the server to only accept local connections if the default user has no password. However, with ACLs set up, external connections are allowed once authenticated.

### Protected Mode and ACL Configuration

Once you have an internal client configured (see [Configuring a Client](#configuring-a-client)), we can configure ACLs while `protected-mode` is still enabled to allow exeternal connections:

1. **Configure ACLs:**
   Connect to the Valkey server and create a new user with a password:
   ```bash
   ./src/valkey-cli -h localhost -p 6379 \
     --tls \
     --cert ./tests/tls/server-alpha.pem \
     --key ./tests/tls/server-alpha.private.pem \
     --cacert ./tests/tls/acme-cert-authority.ca.public.pem
   ```

2. **Create a Default User with a Password:**
   Run the following command in the shell to set up the default user. Setting the `default` user to `OFF` is a security best practice:
   ```plaintext
   ACL SETUSER default OFF >your_secure_password ALLKEYS ALLCOMMANDS
   ```

3. **Create a New User with a Password:**
   Run the following command to create a new user named `valkey_user` with a password. This user will be used with our Valkey client. 
   ```plaintext
   ACL SETUSER valkey_user ON >your_secure_password ALLKEYS ALLCOMMANDS
   ```
   
4. **Verify the User and Permissions:**
   ```plaintext
   ACL LIST
   ```

5. **Connect Using the Password:**
   Use the following command to connect using the password:
   ```bash
   ./src/valkey-cli -h localhost -p 6379 \
     --tls \
     --cert ./tests/tls/server-alpha.pem \
     --key ./tests/tls/server-alpha.private.pem \
     --cacert ./tests/tls/acme-cert-authority.ca.public.pem \
     --user valkey_user
   ```
   
   ```plaintext
   localhost:6379> AUTH valkey_user your_secure_password
   OK
   ```

### Configuring `sysctl.conf` for Memory Overcommit

To enhance memory usage efficiency and reduce the risk of out-of-memory errors in Valkey, it is recommended to set the `vm.overcommit_memory` parameter to 1. This setting allows the kernel to overcommit memory, which can be beneficial for Valkey's performance.

If the `/etc/sysctl.conf` file doesn't already exist on your server's system, you can create it by following these steps:

1. **Create the `sysctl.conf` File:**

   Use a text editor like `nano` to create and edit the file:
   ```bash
   sudo nano /etc/sysctl.conf
   ```

2. **Add the `vm.overcommit_memory` Setting:**

   Add the following line to the file:
   ```plaintext
   vm.overcommit_memory=1
   ```

3. **Apply the Changes Immediately:**

   Run the following command to apply the changes without rebooting:
   ```bash
   sudo sysctl -w vm.overcommit_memory=1
   ```

4. **Verify the Setting:**

   Check if the setting has been applied:
   ```bash
   sysctl vm.overcommit_memory
   ```
   The output should be:
   ```plaintext
   vm.overcommit_memory = 1
   ```
### Configuring PID File Directory
If the server encounters a permission issue when trying to write a PID file to `/var/run/valkey.pid`, you can specify an alternative location for the PID file. Follow these steps:

1. **Create a Subdirectory:**

   Create a subdirectory within `/var/run` where your user can write:
   ```bash
   sudo mkdir /var/run/valkey
   ```

2. **Change Ownership:**

   Change the ownership of the directory to the user `valkeyuser`:
   ```bash
   sudo chown valkeyuser:valkeyuser /var/run/valkey
   ```

3. **Change Permissions:**

   Ensure that your user has read/write permissions:
   ```bash
   sudo chmod 755 /var/run/valkey
   ```

## Configuring Server

To start the Valkey server with TLS enabled, use the following command:
```
./src/valkey-server /path/to/valkey.conf --tls-port 6379 --port 0 \
  --tls-cert-file ./tests/tls/server-alpha.pem \
  --tls-key-file ./tests/tls/server-alpha.private.pem \
  --tls-ca-cert-file ./tests/tls/acme-cert-authority.ca.public.pem \
  --pidfile /var/run/valkey/valkey.pid
  --loglevel debug
```

**Explanation of Command-Line Arguments:**

- `/path/to/valkey.conf`: Path to the Valkey configuration file.
- `tls-port 6379`: Port for TLS connections.
- `port 0`: Disables non-TLS port.
- `tls-cert-file`: Path to the server's TLS certificate file.
- `tls-key-file`: Path to the server's TLS key file.
- `tls-ca-cert-file`: Path to the CA certificate file.
- `pidfile /var/run/valkey/valkey.pid`: Path to the PID file.
- `loglevel debug`: Sets the logging level to debug for detailed output.

The console should display the following:

```plaintext
3292:C 04 Jun 2024 00:36:35.094 * oO0OoO0OoO0Oo Valkey is starting oO0OoO0OoO0Oo
3292:C 04 Jun 2024 00:36:35.094 * Valkey version=255.255.255, bits=64, commit=efa8ba51, modified=0, pid=3292, just started
3292:C 04 Jun 2024 00:36:35.094 * Configuration loaded
3292:M 04 Jun 2024 00:36:35.095 * Increased maximum number of open files to 10032 (it was originally set to 1024).
3292:M 04 Jun 2024 00:36:35.095 * monotonic clock: POSIX clock_gettime
                .+^+.
            .+#########+.
        .+########+########+.           Valkey 255.255.255 (efa8ba51/0) 64 bit
    .+########+'     '+########+.
 .########+'     .+.     '+########.    Running in standalone mode
 |####+'     .+#######+.     '+####|    Port: 6379
 |###|   .+###############+.   |###|    PID: 3292
 |###|   |#####*'' ''*#####|   |###|
 |###|   |####'  .-.  '####|   |###|
 |###|   |###(  (@@@)  )###|   |###|          https://valkey.io
 |###|   |####.  '-'  .####|   |###|
 |###|   |#####*.   .*#####|   |###|
 |###|   '+#####|   |#####+'   |###|
 |####+.     +##|   |#+'     .+####|
 '#######+   |##|        .+########'
    '+###|   |##|    .+########+'
        '|   |####+########+'
             +#########+'
                '+v+'

3292:M 04 Jun 2024 00:36:35.098 * Server initialized
3292:M 04 Jun 2024 00:36:35.098 . The AOF directory appendonlydir doesn't exist
3292:M 04 Jun 2024 00:36:35.098 * Loading RDB produced by valkey version 255.255.255
3292:M 04 Jun 2024 00:36:35.098 * RDB age 112 seconds
3292:M 04 Jun 2024 00:36:35.098 * RDB memory usage when created 0.99 Mb
3292:M 04 Jun 2024 00:36:35.098 * Done loading RDB, keys loaded: 2, keys expired: 0.
3292:M 04 Jun 2024 00:36:35.098 * DB loaded from disk: 0.000 seconds
3292:M 04 Jun 2024 00:36:35.098 * Ready to accept connections tls
3292:M 04 Jun 2024 00:36:35.099 - DB 0: 2 keys (0 volatile) in 4 slots HT.
3292:M 04 Jun 2024 00:36:35.099 . 0 clients connected (0 replicas), 989976 bytes in use
```

**Potential Errors**

- If the following error appears in the output: `Memory overcommit must be enabled!`, it indicates that you have not configured `sysctl.conf` correctly. See [Configuring `sysctl.conf` for Memory Overcommit](#configuring-sysctlconf-for-memory-overcommit).
- If the following error appears in the output: `Failed to write PID file: Permission denied`, it indicates that the server doesn't have permissions to write to the directory where the PID file is being stored. See [Configuring PID File Directory](#configuring-pid-file-directory).

### Verify Server is Listening

1. **Check Listening Ports:**
   ```bash
   netstat -tuln | grep 6379
   ```
   Example output:
   ```plaintext
   valkeyuser@server-alpha:~/valkey$ netstat -tuln | grep 6379
   tcp        0      0 0.0.0.0:6379            0.0.0.0:*               LISTEN
   ```
   **Explanation:**

   - `tcp`: Indicates the protocol as TCP. This does not mean TLS is misconfigured; TLS runs on top of TCP.
   - `0.0.0.0:6379`: Shows that the server is listening on all network interfaces on port 6379.
   - `LISTEN`: Indicates that the port is open and ready to accept connections.

2. **Check Running Processes:**

Use the `ps` command to check if the Valkey server process is running.
   ```bash
   ps aux | grep valkey-server
   ```
   
   Example output:
   
   ```plaintext
    valkeyuser@server-alpha:~/valkey$ ps aux | grep valkey-server
    valkeyuser+    3609  0.3  0.0 135236 11876 pts/3    Sl+  01:58   0:00 ./src/valkey-server 0.0.0.0:6379
    valkeyuser+    3636  0.0  0.0   6612  2240 pts/2    S+   01:58   0:00 grep --color=auto valkey-server
   ```
   **Explanation:**
   
   - `valkeyuser+ 3609`: Shows the username and process ID (PID) of the running Valkey server. `0.3 0.0`: Indicates the CPU and memory usage of the process.
   - `./src/valkey-server 0.0.0.0:6379`: Shows the command used to start the Valkey server, confirming that it is running on port 6379.
   - The second line is the `grep` command itself, which is filtering the `ps` output to show only the Valkey server process.

## Configuring a Client

The Valkey command line interface (`valkey-cli`) is a terminal program used to send commands to and receive replies from the Valkey server. It operates in two main modes:

1. Interactive REPL mode for typing commands and receiving replies.
2. Command mode for executing commands with arguments and printing replies to standard output.

### Connection with an Internal Client

Use the `valkey-cli` command to connect to the Valkey server running on the same machine with TLS enabled.

```bash
valkeyuser@server-alpha:~/valkey$ ./src/valkey-cli --tls \
  --cert ./tests/tls/server-alpha.pem \
  --key ./tests/tls/server-alpha.private.pem \
  --cacert ./tests/tls/acme-cert-authority.ca.public.pem \
  -h localhost \
  -p 6379 \ 
  PING
PONG
```

**Explanation:**

- `--tls`: Enables TLS encryption for the connection.
- `--cert`: Specifies the path to the client's TLS certificate.
- `--key`: Specifies the path to the client's TLS private key.
- `--cacert`: Specifies the path to the CA certificate.
- `-h localhost`: Specifies the host (localhost in this case).
- `-p 6379`: Specifies the port (6379 in this case).

### Example Output on the Server Side:

```plaintext
3268:M 04 Jun 2024 00:31:14.668 - Accepted 127.0.0.1:58192
3268:M 04 Jun 2024 00:31:15.146 - DB 0: 2 keys (0 volatile) in 4 slots HT.
3268:M 04 Jun 2024 00:31:15.146 . 1 clients connected (0 replicas), 1037504 bytes in use
```

### Troubleshooting Client

Use the `valkey-cli` command to check the TLS configuration of your Valkey server.
Example session:

```plaintext
valkeyuser@server-alpha:~/valkey$ ./src/valkey-cli

 --tls \
  --cert ./tests/tls/server-alpha.pem \
  --key ./tests/tls/server-alpha.private.pem \
  --cacert ./tests/tls/acme-cert-authority.ca.public.pem \
  -h localhost \
  -p 6379 \
  CONFIG GET tls-auth-clients
1) "tls-auth-clients"
2) "yes"
```

**Explanation:**

- If `tls-auth-clients` is set to `yes`, it means that the server requires clients to authenticate using TLS certificates.

Use the `valkey-cli` command to retrieve the current TLS configuration of your Valkey server.

```plaintext
  valkeyuser@server-alpha:~/valkey$ ./src/valkey-cli --tls \
  --cert ./tests/tls/server-alpha.pem \
  --key ./tests/tls/server-alpha.private.pem \
  --cacert ./tests/tls/acme-cert-authority.ca.public.pem \
  -h localhost \
  -p 6379 \
  CONFIG GET tls*
```

**Example output:**

```plaintext
1) "tls-key-file"
2) "./tests/tls/server-alpha.private.pem"
3) "tls-port"
4) "6379"
5) "tls-auth-clients"
6) "yes"
7) "tls-session-caching"
8) "yes"
9) "tls-session-cache-timeout"
10) "300"
11) "tls-ca-cert-file"
12) "./tests/tls/acme-cert-authority.ca.public.pem"
13) "tls-cert-file"
14) "./tests/tls/server-alpha.pem"
```

### Connecting an External Client

#### 1. Configuring Client on a Seperate Linux Machine

Here, we refer to the different linux machine as **`client-beta`**.

1. **Install Required Packages:**

   Open the command line and install the necessary packages:

   ```bash
   sudo apt-get update
   sudo apt-get install expect libssl-dev pkg-config gcc g++ make openssl build-essential
   ```

2. **Connect to Server:**

   Use the `valkey-cli` command to connect to the Valkey server running on `server-alpha` from `client-beta` with TLS enabled:

   ```bash
   ./src/valkey-cli --tls \
     --cert ./tests/tls/client-beta.pem \
     --key ./tests/tls/client-beta.private.pem \
     --cacert ./tests/tls/acme-cert-authority.ca.public.pem \
     -h server-alpha.network.local \
     -p 6379 
   ```

#### 2. Configuring Client on Windows

Here, we refer to the different linux machine as **`client-gamma`**.

1. **Set Up the Ubuntu App:**

   - **Install the Ubuntu App:**

     Install the Ubuntu app using WSL or download it from the Microsoft Store:

     ```bash
     wsl --install -d ubuntu
     ```

2. **Ensure Packages are Installed:**

   Open the Ubuntu app and install the necessary packages:

   ```bash
   sudo apt-get update
   sudo apt-get install expect libssl-dev pkg-config gcc g++ make openssl build-essential
   ```

3. **Connect to Server:**

   Use the following command in your chosen environment (Ubuntu app or Git Bash) to connect to the Valkey server from `client-gamma`:

   ```bash
   ./src/valkey-cli --tls \
     --cert /path/to/client-gamma.pem \
     --key /path/to/client-gamma.private.pem \
     --cacert /path/to/acme-cert-authority.ca.public.pem \
     -h server-alpha.network.local \
     -p 6379 
   ```

## Monitoring

### Write Script to Collect Metrics

1. **Write Script to Collect Metrics:**
   On `client-gamma`, create a script to collect CPU and memory usage metrics and send them to the Valkey server, `server-alpha`.

   ```bash
   #!/bin/bash

   while true; do
     # Collect CPU usage
     cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
     
     # Collect memory usage
     memory_usage=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }')
     
     echo "CPU Usage: $cpu_usage"
     echo "Memory Usage: $memory_usage"

     # Send data to Valkey server
     ./src/valkey-cli --tls \
       --cert /path/to/client-gamma.pem \
       --key /path/to/client-gamma.private.pem \
       --cacert /path/to/acme-cert-authority.ca.public.pem \
       --user "$VALKEY_USERNAME" \
       -h server-alpha.network.local \
       -p 6379 \
       -a "$VALKEY_PASSWORD" \
       SET cpu_usage $cpu_usage
     
     ./src/valkey-cli --tls \
       --cert /path/to/client-gamma.pem \
       --key /path/to/client-gamma.private.pem \
       --cacert /path/to/acme-cert-authority.ca.public.pem \
       --user "$VALKEY_USERNAME" \
       -h server-alpha.network.local \
       -p 6379 \
       -a "$VALKEY_PASSWORD" \
       SET memory_usage $memory_usage

     sleep 60
   done
   ```
   
### Test the Monitoring Script

First, ensure that `server-alpha` is running the Valkey Server.

1. **Make the Script Executable:**
   Change the permissions of the script to make it executable.
   ```bash
   chmod +x ~/monitoring_script.sh
   ```

2. **Run the Script:**
   Execute the monitoring script to start collecting and sending metrics.
   ```bash
   ./monitoring_script.sh
   ```

   Example output:
   ```plaintext
   CPU Usage: 7.4
   Memory Usage: 69.70
   OK
   OK
   CPU Usage: 6.2
   Memory Usage: 68.73
   OK
   OK
   CPU Usage: 7.5
   Memory Usage: 69.18
   ```

3. **Check the Output on the Server Machine:**
   On the server machine `server-alpha`, use a client to verify that the metrics were received and stored correctly.
   ```bash
   ./src/valkey-cli --tls \
     --cert ./tests/tls/server-alpha.pem \
     --key ./tests/tls/server-alpha.private.pem \
     --cacert ./tests/tls/acme-cert-authority.ca.public.pem \
     -h localhost \
     -p 6379 GET memory_usage
   ```

   Example output:
   ```plaintext
   "69.18"
   ```

### Configuring systemd

Systemd services can manage various tasks and processes for our server in the background, ensuring that they run continuously and restart automatically if they fail.

1. **Copy the Template for the Valkey Server Service File:**

   Copy the template file to the systemd directory using the `cp` command:
   ```bash
   sudo cp /home/valkeyuser/valkey/utils/systemd-valkey_server.service /etc/systemd/system/valkey-server.service
   ```

2. **Edit the Copied Service File:**

   Open the copied service file for editing:
   ```bash
   sudo vi /etc/systemd/system/valkey-server.service
   ```

3. **Configure the `.service` File:**

   Modify the service file with the appropriate configuration:
   ```plaintext
   [Unit]
   Description=Valkey data structure server
   Documentation=https://github.com/valkey-io/valkey-doc
   Wants=network-online.target
   After=network-online.target

   [Service]
   ExecStart=/home/valkeyuser/valkey/src/valkey-server /home/valkeyuser/valkey/valkey.conf --tls-port 6379 --port 0 --tls-cert-file /home/valkeyuser/valkey/tests/tls/server-alpha.pem --tls-key-file /home/valkeyuser/valkey/tests/tls/server-alpha.private.pem --tls-ca-cert-file /home/valkeyuser/valkey/tests/tls/acme-cert-authority.ca.public.pem
   LimitNOFILE=10032
   NoNewPrivileges=yes
   Type=notify
   TimeoutStartSec=infinity
   TimeoutStopSec=infinity
   UMask=0077
   User=valkeyuser

   [Install]
   WantedBy=multi-user.target
   ```

4. **Reload the systemd Manager Configuration:**

   Reload the systemd manager configuration to apply the changes:
   ```bash
   sudo systemctl daemon-reload
   ```

5. **Enable the Service to Start at Boot:**

   Enable the service to start at boot:
   ```bash
   sudo systemctl enable valkey-server
   ```

6. **Start the Service:**

   Start the Valkey server service:
   ```bash
   sudo systemctl start valkey-server
   ```

7. **Adjust Permissions if Necessary:**

   If the TLS directory and certificates do not have the correct permissions, update them to allow access. Ensure the `valkeyuser` user has read and execute permissions on the directory:
   ```bash
   sudo chown -R valkeyuser:valkeyuser /home/valkeyuser/valkey
   sudo chmod 755 /home/valkeyuser/valkey/tests/tls
   sudo chmod 644 /home/valkeyuser/valkey/tests/tls/server-alpha.pem
   sudo chmod 600 /home/valkeyuser/valkey/tests/tls/server-alpha.private.pem
   sudo chmod 644 /home/valkeyuser/valkey/tests/tls/acme-cert-authority.ca.public.pem
   ```

8. **Verify the Ownership of the TLS Directory:**

   Ensure the `valkeyuser` user owns the directory:
   ```bash
   sudo chown valkeyuser:valkeyuser /home/valkeyuser/valkey/tests/tls
   ```

9. **Check the Status of the Service:**

   Verify that the service is running correctly:
   ```bash
   sudo systemctl status valkey-server
   ```

   Example output:
   ```plaintext
   valkeyuser@server-alpha:~$ sudo systemctl status valkey-server
   ● valkey-server.service - Valkey data structure server
        Loaded: loaded (/etc/systemd/system/valkey-server.service; enabled; vendor preset: enabled)
        Active: activating (start) since Wed 2024-06-05 00:23:51 UTC; 24min ago
          Docs: https://github.com/valkey-io/valkey-doc
      Main PID: 5856 (valkey-server)
         Tasks: 6 (limit: 38306)
        Memory: 4.0M
           CPU: 5.651s
        CGroup: /system.slice/valkey-server.service
                └─5856 "/home/valkeyuser/valkey/src/valkey-server 0.0.0.0:6379" "" "" "" "" "" "" "" "" "" "" "" "" "" "" ">

   Jun 05 00:47:48 server-alpha.network.local valkey-server[5856]: 5856:M 05 Jun 2024 00:47:48.848 - DB 0: 2 keys (0 volatile) i>
   Jun 05 00:47:48 server-alpha.network.local valkey-server[5856]: 5856:M 05 Jun 2024 00:47:48.848 . 1 clients connected (0 repl>
   ```

10. **View the Logs if There are Issues:**

    If there are issues, view the logs for more details:
    ```bash
    sudo journalctl -u valkey-server.service
    ```
