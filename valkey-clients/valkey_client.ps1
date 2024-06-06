$valkeyClientPath = "/home/valkeyuser/valkey/src/valkey-cli"
$certPath = "/home/valkeyuser/valkey/tests/tls/client-gamma.pem"
$keyPath = "/home/valkeyuser/valkey/tests/tls/client-gamma.private.pem"
$cacertPath = "/home/valkeyuser/valkey/tests/tls/acme-cert-authority.ca.public.pem"
$serverHost = "server-alpha.network.local"
$port = 6379

$baseCommand = "wsl $valkeyClientPath --tls --cert $certPath --key $keyPath --cacert $cacertPath -h $serverHost -p $port"

function Invoke-CommandSafely {
    param (
        [string]$command
    )
    Write-Host "Running command: $command"
    try {
        $result = Invoke-Expression $command
        return $result
    } catch {
        Write-Host "Error running command: $_"
        return $null
    }
}

$pingCommand = "$baseCommand PING"
Write-Host "Ping Command: $pingCommand"
$pingResult = Invoke-CommandSafely -command $pingCommand
Write-Host "Ping Result: $pingResult"

$getMemoryUsageCommand = "$baseCommand GET memory_usage"
Write-Host "Get Memory Usage Command: $getMemoryUsageCommand"
$memoryUsageResult = Invoke-CommandSafely -command $getMemoryUsageCommand
Write-Host "Memory Usage Result: $memoryUsageResult"
