$pings=@'
192.168.1.25 printer
192.168.1.26 nas
'@

ForEach ($line in $($pings -split "`r`n")){
    $IP_HOST =$line.Split(" ")
    $ping = New-Object System.Net.Networkinformation.Ping
    $response = $ping.send($IP_HOST[0]) | select status
 
    if ($response -Match "Success"){
        [byte[]]$bytes  = [text.Encoding]::UTF8.GetBytes($IP_HOST[1])

        $tcpClient = New-Object System.Net.Sockets.TCPClient
        $tcpClient.Connect("127.0.0.1",50051)

        $clientStream = $tcpClient.GetStream()
        $clientStream.Write($bytes,0,$bytes.length)
        $tcpClient.Close()
    }
}