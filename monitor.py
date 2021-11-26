# Emails that will recieve the Alerts
# You can have multiple emails in the array
receiver = ["your@email.com"] 

# Email that will be sending Alerts
# Must have login from unsafe sources activated
sender_email = "Sender@gmail.com"
password = "yourpassword"

# Seconds that a host must be down before reporting Down Status
waittime = 600
	

# =====
# Utils
# =====
from datetime import datetime
from collections import OrderedDict
import unicodedata

intervals = (
	('weeks', 604800),  # 60 * 60 * 24 * 7
	('days', 86400),    # 60 * 60 * 24
	('hours', 3600),    # 60 * 60
	('minutes', 60),
	('seconds', 1),
)

# Turns seconds into human readable (4 hours 13 minutes 12 seconds...)
def display_time(seconds, granularity=3):
	result = []
	for name, count in intervals:
		value = seconds // count
		if value:
			seconds -= value * count
			if value == 1:
				name = name.rstrip('s')
			result.append("{} {}".format(value, name))
	return ', '.join(result[:granularity])

def Epoch():
	return int(datetime.now().timestamp())

# Returns how much time a host was down
def TimeDown(server_name):
	global Servers_Down
	downtime_epoch = Servers_Down[server_name] 
	total = Epoch() - downtime_epoch
	# Human readable
	return display_time(total,3)

def UpTime(server_name):
	global Servers_Up
	uptime_epoch = Servers_Up[server_name]
	return Epoch2Date(uptime_epoch, True)

def Epoch2Date(epoch, log=True):
	date = datetime.fromtimestamp(epoch)
	if log:
		return  f'[{date.strftime("%d/%m/%y %H:%M:%S")}]'
	return date.strftime("%d/%m/%y %H:%M:%S")

def Logdate():
	now = datetime.now()
	return f'[{now.strftime("%d/%m/%y %H:%M:%S")}]'

def UTF2ASCII(input_str):
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	only_ascii = nfkd_form.encode('ASCII', 'ignore')
	return only_ascii


# ============
# Email Sender
# ============
import smtplib, ssl

def SendEmail(server_name, status, ip, mensaje_adicional=""):
	global receiver, sedner_email, password
	smtp_server = "smtp.gmail.com"
	smtp_port = 587  # For starttls

	# Don't touch identation
	message = UTF2ASCII(f"""From: Server Monitor <{sender_email}>
To: <{receiver}>
Subject: [ALERT] {server_name} {status}

Server: {server_name} - {ip}
Status: {status}
{mensaje_adicional}
""")
	# Create a secure SSL context
	context = ssl.create_default_context()
	# Try to log in to server and send email
	try:
		server = smtplib.SMTP(smtp_server,smtp_port)
		server.ehlo()
		server.starttls(context=context) # Secure the connection
		server.ehlo()
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver, message)
		print(Logdate(), f"[Email] correctly sent for", server_name, f"Status: {status}")

	except Exception as e:
		# Print any error messages to stdout
		print(Logdate(), "Error sending email", e)
	finally:
		server.quit() 


# ==============
# Server Monitor
# ==============

ACL = []
Servers_Up = {}
Servers_Down = {}

def UpdateACL():
	global ACL
	ACL = [host.strip() for host in open("ACL.txt", "r").readlines()]
	return 

def ThreadedMonitor(connection, ip, port):
	global Servers_Up, Servers_Down, ACL, waittime

	# Save connection epoch (time)
	conn_epoch = Epoch()
	server_name = connection.recv(2048)
	connection.close()

	server_name = server_name.decode('utf-8')
	server_name_ip = f"{server_name} - {ip}"

	# Update ACL with potentially new added hosts
	if server_name not in ACL:
		UpdateACL()

	# If host is authorized
	if server_name in ACL:
		Servers_Up[server_name] = conn_epoch
		print(Logdate(), '[Online]',f"{server_name_ip}:{port}")

		# Check if the server was Down
		if server_name in Servers_Down:
			downtime = TimeDown(server_name)
			del Servers_Down[server_name]
			print(Logdate(), '[Online Again]', server_name, f'Online after {downtime} without connection ')
			SendEmail(server_name, "Online", ip, f"Downtime: {downtime}")
		
		# Wait n seconds. New thread should change epoch before timeup.
		time.sleep(waittime) # 600 in production
		# Check in case a different thread already detected the host Down.
		if (server_name in Servers_Up):
			# If epoch didn't change, the host is down.
			if (Servers_Up[server_name] == conn_epoch):
				print(Logdate(), '[Down]', server_name_ip)
				del Servers_Up[server_name]
				Servers_Down[server_name] = Epoch()
				SendEmail(server_name, "Down", ip)
	else:
		print(Logdate(), '[Alert] Unauthorized Connection (add to ACL)', server_name_ip)


# ===============
# Website Monitor
# ===============

def MonitorWeb():
	from flask import Flask, render_template
	from waitress import serve
	app = Flask(__name__, template_folder='templates/')

	@app.route("/")
	def monitor():  
		offline = [host for host in ACL if host not in Servers_Up and host not in Servers_Down]
		                 # List [down hour, down time]
		downtime = {host:[Epoch2Date(Servers_Down[host], True), TimeDown(host)] for host in Servers_Down}
		                                        # Creates the dict in ACL order 
		uptime = OrderedDict({host:UpTime(host) for host in ACL if host in Servers_Up})

		return render_template('template.html', offline=offline,\
		                       downtime=downtime, uptime=uptime ) #**locals() # Returns all local variables

	start_new_thread(lambda: serve(app,host="127.0.0.1", port=80),())
	

# ==================
# Connection Handler
# ==================
import socket, os, time
from _thread import *

def MonitorServer():
	ServerSocket = socket.socket()
	host = '0.0.0.0'
	port = 50051
	try:
		ServerSocket.bind((host, port))
		print(Logdate(),'Server Monitor Started..')
		ServerSocket.listen(5)
		UpdateACL()
	except socket.error as e:
		print(str(e))
		exit(0)

	while True:
		Client, address = ServerSocket.accept()        # IP   Port
		start_new_thread(ThreadedMonitor, (Client,address[0],address[1]))
	ServerSocket.close()

# ==============
# Main Execution
# ==============

MonitorWeb()
MonitorServer()
