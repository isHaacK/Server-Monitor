$Text = "PC-NAME1"
[byte[]]$bytes  = [text.Encoding]::UTF8.GetBytes($Text)

$tcpClient = New-Object System.Net.Sockets.TCPClient
$tcpClient.Connect("127.0.0.1",50051)

$clientStream = $tcpClient.GetStream()
$clientStream.Write($bytes,0,$bytes.length)
$tcpClient.Close()