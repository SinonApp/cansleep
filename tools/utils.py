from os import path
import requests
from datetime import datetime
import ipaddress
import re
from pathlib import Path
from typing import List
import shodan
import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    bold_grey = "\x1b[38;1m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '[%(asctime)s] [%(levelname)s] %(message)s'

    FORMATS = {
        logging.DEBUG: bold_red + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

def get_location(ip_address):
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region_code": response.get("region_code"),
        "country_name": response.get("country_name"),
        'country_code': response.get("country_code"),
    }
    return location_data

def search_shodan(country, save_path, api, logging, city=None, mode=None, port=None):
    if mode == None: return None
    data = ''
    match mode:
        case 'dahua':
            mode = 'Dahua DVR'
        case 'hikka':
            mode = 'HikVision'
        case 'rtsp':
            mode = 'RTSP 200'

    if port:
        mode += f' port:{port}'

    api = shodan.Shodan(api)
    logging.debug(f'[SHODAN] Search: country:"{country}" city:"{city}" {mode}')
    results = api.search(f'country:"{country}" city:"{city}" {mode}')

    logging.info(f'[SHODAN] Found {len(results["matches"])} mathces')

    for result in results['matches']:
        data += f'{result["ip_str"]}\n'

    with open(save_path, 'w') as file:
        file.write(data)

def get_geo_by_ip(ip_address, api):
    try:
        api = shodan.Shodan(api)
        info = api.host(ip_address)

        return [
            info['latitude'],
            info['longitude'],
            info['country_code'],
            info['country_name'],
            info['region_code'],
            info['city']
        ]
    except:
        info = get_location(ip_address)
        try:
            return [
                None,
                None,
                info['country_code'],
                info['country_name'],
                info['region_code'],
                info['city']
            ]
        except:
            return [
                None,
                None,
                None,
                None,
                None,
                None,
            ]

def load_from_report(report_path):
    report = []
    with open(report_path) as report_file:
        for line in report_file.readlines():
            report.append(line.replace('\n', ''))

    return report

def write_loot(data, loot_path, proto=None, api_key=None):
    if data:
        write = ''
        i = 0
        for i, target in enumerate(data):
            if target:
                ip = target[0]
                port = target[1]
                login = target[2]
                password = target[3]

                if api_key:
                    geo = get_geo_by_ip(ip, api_key)
                    write += f'{proto};{ip};{port};{login};{password};{geo[0]};{geo[1]};{geo[2]};{geo[3]}\n'
                else:
                    write += f'{proto};{ip};{port};{login};{password};None;None;None;None\n'

        with open(loot_path, 'a') as loot:
            loot.write(write)

        if write == '': return False
        return i
    return False

def target_is_file(target):
    if path.exists(target):
        return True
    return False

def dtfilename():
    return str(datetime.now()).replace(':', '-').split('.')[0].replace(' ', '_')

def create_folder(path: Path):
    path.mkdir(parents=True)

def create_file(path: Path):
    path.touch()

def escape_chars(s: str):
    # Escape every character that's not a letter,
    # '_', '-', '.' or space with an '_'.
    return re.sub(r"[^\w\-_. ]", "_", s)

def find(var: str, response: str):
    """Searches for `var` in `response`."""
    reg = {
        "realm": re.compile(r'realm="(.*?)"'),
        "nonce": re.compile(r'nonce="(.*?)"'),
    }
    match = reg[var].search(response)
    if match:
        return match.group(1)
    else:
        return ""

def get_lines(path: Path) -> List[str]:
    return path.read_text().splitlines()

def parse_input_line(input_line: str) -> List[str]:
    """
    Parse input line and return list with IPs.

    Supported inputs:

        1) 1.2.3.4
        2) 192.168.0.0/24
        3) 1.2.3.4 - 5.6.7.8
    Any non-ip value will be ignored.
    """
    try:
        # Input is in range form ("1.2.3.4 - 5.6.7.8"):
        if "-" in input_line:
            input_ips = input_line.split("-")
            ranges = [
                ipaddr
                for ipaddr in ipaddress.summarize_address_range(
                    ipaddress.IPv4Address(input_ips[0].strip()),
                    ipaddress.IPv4Address(input_ips[1].strip()),
                )
            ]
            return [str(ip) for r in ranges for ip in r]

        # Input is in CIDR form ("192.168.0.0/24"):
        elif "/" in input_line:
            network = ipaddress.ip_network(input_line)
            return [str(ip) for ip in network]

        # Input is a single ip ("1.1.1.1"):
        else:
            ip = ipaddress.ip_address(input_line)
            return [str(ip)]
    except ValueError:
        # If we get any non-ip value just ignore it
        return []

def load_txt(path: Path, name: str) -> List[str]:
    result = []
    if name == "credentials":
        result = [line.strip("\t\r") for line in get_lines(path)]
    elif name == "routes":
        result = get_lines(path)
    elif name == "targets":
        result = [
            target for line in get_lines(path) for target in parse_input_line(line)
        ]
    return result