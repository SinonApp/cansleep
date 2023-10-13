import subprocess
import re
import sys
import os

class SmapScanner():

    def __init__(self, target, is_file=False, ports=[], options=None, logging=None):
        self.target = target
        self.is_file = is_file
        self.ports = ports
        self.options = options

    def check_os(self):
        if os.name == 'nt':
            return False
        return True

    def prepare_command_linux(self):
        if self.options != None:
            self.command = 'smap -p' + ','.join(list(map(str, self.ports))) + ' ' + ' '.join(self.options)
        else:
            self.command = 'smap -p' + ','.join(list(map(str, self.ports)))

        if self.is_file:
            self.command += ' -iL ' + self.target
        else:
            self.command += ' ' + self.target

    def prepare_command_windows(self):
        if self.options != None:
            self.command = './lib/smap.exe -p' + ','.join(list(map(str, self.ports))) + ' ' + ' '.join(self.options)
        else:
            self.command = './lib/smap.exe -p' + ','.join(list(map(str, self.ports)))

        if self.is_file:
            self.command += ' -iL ' + self.target
        else:
            self.command += ' ' + self.target

    def scan_smap(self):
        data = subprocess.check_output(self.command.split())
        return data.decode()

    def parse_smap(self, output):
        data = {}
        ip_address = None
        for line in output.split('\n'):
            if 'Nmap scan report for' in line:
                re_ip_address = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if len(re_ip_address) != 0:
                    ip_address = re_ip_address[0]
                data[ip_address] = []
            elif 'open' in line and ip_address != None:
                data[ip_address].append(int(line.split('/tcp')[0]))
        return data
    
    def scan(self):
        if self.check_os():
            self.prepare_command_linux()
        else:
            self.prepare_command_windows()
        output = self.scan_smap()
        data = self.parse_smap(output)
        
        output = ''
        for ip in data:
            for port in data[ip]:
                output += f'{ip}:{port}\n'

        return output
