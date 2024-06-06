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
    -h server-alpha.network.local \
    -p 6379 SET cpu_usage $cpu_usage
  
  ./src/valkey-cli --tls \
    --cert /path/to/client-gamma.pem \
    --key /path/to/client-gamma.private.pem \
    --cacert /path/to/acme-cert-authority.ca.public.pem \
    -h server-alpha.network.local \
    -p 6379 SET memory_usage $memory_usage

  sleep 60
done
