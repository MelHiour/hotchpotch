#!/usr/bin/env python

import SocketServer
import beanstalkc
import json
import re

HOST, PORT = "0.0.0.0", 10514
BHOST, BPORT = "localhost", 11300

try:
    beanstalk = beanstalkc.Connection(host=BHOST, port=BPORT)
except beanstalkc.BeanstalkcException as e:
    print(f"Error connecting to Beanstalkd: {e}")
    exit(1)

def password_failed(host, data):
    result = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", data)
    if result:
        job = {'host': host, 'type': 'password_failed', 'from': result.group()}
        return job
    return None

def interface_down(host, data):
    result = re.search(r"eth\d+", data)
    if result:
        job = {'host': host, 'type': 'interface_down', 'interface': result.group()}
        return job
    return None
    
TRIGGERS = {'Failed password for root': password_failed,
            'Failed password for invalid user': password_failed,
            'state DOWN': interface_down
           }

class SyslogTCPHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline().strip()
        if not data:
            return
			
        try:
            message_parts = data.split()
            host = message_parts[2]
        except IndexError:
            host = "unknown"

        for trigger, handler in TRIGGERS.items():
            if trigger in data:
                job = handler(host, data)
                
                if job:
                    print(job)
                    try:
                        beanstalk.put(json.dumps(job))
                    except beanstalkc.BeanstalkcException as e:
                        print(f"Error putting job on Beanstalkd: {e}")
                
if __name__ == "__main__":
    try:
        server = SocketServer.TCPServer((HOST, PORT), SyslogTCPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("Crtl+C Pressed. Shutting down.")
