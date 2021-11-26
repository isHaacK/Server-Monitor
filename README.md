# Server-Monitor
Server with web interface to monitor the status of hosts in real time. Send emails when hosts go down or reconnect.
Useful for sysadmins that want to know when a Host goes offline.
## Usage
- Configure the emails in monitor.py
- Set a scheduled task on the desired hosts every 5 minutes to run the ps1 file.
- Update the ACL with any new host names.
## Features
- Send email everytime a host is down.
- Send email when a host that went down is up again. shows downtime
- Web interface shows Online and Down hosts. if host is down, shows the current downtime.
## Web interface 
![image](https://user-images.githubusercontent.com/43073766/143605084-801a4213-141e-4b9f-91b8-6e62090a44b3.png)
## To do
add client for linux
