# Server-Monitor
Server with web interface to monitor the status of hosts in real time. Send emails when hosts go down or reconnect.
Useful for sysadmins that want to know when a Host goes offline.
## Usage
- Configure the emails in monitor.py
- Set a scheduled task on the desired hosts every 5 minutes to run the ps1 file.
  - client.ps1 report status of the host that is executing it.
  - ping_multi_client.ps1 pings any ip (like printers) and report its stauts.
- Update the ACL with any new host names.
## Features
- Send email everytime a host is down.
- Send email when a host that went down is up again. shows downtime
- Web interface.
  - Down: Shows last ping and the current downtime of a host.
  - Online: Shows last online ping.
  - Offline: Hosts in ACL that have not recieved a connection since Server Monitor started.
## Web interface 
![image](https://user-images.githubusercontent.com/43073766/143618169-94a9afea-b247-4e0d-b510-caf66f1a7a52.png)
## To do
add client for linux
