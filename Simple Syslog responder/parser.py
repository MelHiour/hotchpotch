#!/usr/bin/env python

import SocketServer
import beanstalkc
import json
import re

HOST, PORT = "0.0.0.0", 10514
BHOST, BPORT = "localhost", 11300

def password_failed(host, data):
	result = re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", data)
	job = {'host':host,'type':'password_failed','from':result.group()}
	return job

def interface_down(host, data):
	result = re.search("\eth\d", data)
	job = {'host':host,'type':'interface_down','interface':result.group()}
	return job
	
TRIGGERS = {'Failed password for root':password_failed,
	    'Failed password for invalid user':password_failed,
	    'state DOWN':interface_down
	   }

class SyslogTCPHandler(SocketServer.StreamRequestHandler):
	def handle(self):
		proxy_data = self.rfile.readline().strip()
		data = self.rfile.readline().strip()
		for trigger,handler in TRIGGERS.items():
			if trigger in data:
				job = handler(proxy_data.split()[2], str(data))
				print(job)
				beanstalk = beanstalkc.Connection(host=BHOST, port=BPORT)
				beanstalk.put(json.dumps(job))

if __name__ == "__main__":
	try:
		server = SocketServer.TCPServer((HOST,PORT), SyslogTCPHandler)
		server.serve_forever(poll_interval=0.5)
	except (IOError, SystemExit):
		raise
	except KeyboardInterrupt:
		print ("Crtl+C Pressed. Shutting down.")
