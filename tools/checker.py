from connectors.rtsp import RTSPClient, rtsp_connect
import requests
import struct
import socket
import time

def rtsp_checker(ip, ports, routes, logging):
    DUMMY_ROUTE = "/0x8b6c42"
    ROUTE_OK_CODES = [
        "RTSP/1.0 200",
        "RTSP/1.0 401",
        "RTSP/1.0 403",
        "RTSP/2.0 200",
        "RTSP/2.0 401",
        "RTSP/2.0 403",
    ]

    target = RTSPClient(ip)
    for port in ports:
        ok = rtsp_connect(target, port=port, route=DUMMY_ROUTE)
        if ok and any(code in target.data for code in ROUTE_OK_CODES):
            target.port = port
            target.routes.append("/")
            logging.info(f'[RTSP] Route found for: {target}')
            return target

        for route in routes:
            ok = rtsp_connect(target, port=port, route=route)
            if not ok:
                logging.debug(f'[RTSP] Target {target} failed checked')
                break
            if any(code in target.data for code in ROUTE_OK_CODES):
                target.port = port
                target.routes.append(route)
                logging.info(f'[RTSP] Route found for: {target}')
                return target

def dahua_checker(target, logging):
    if not target: return False
    ip, port = target.split(':')

    LOGIN_TEMPLATE = b'\xa0\x00\x00\x60%b\x00\x00\x00%b%b%b%b\x04\x01\x00\x00\x00\x00\xa1\xaa%b&&%b\x00Random:%b\r\n\r\n'
    login = 'asd'
    password = 'asd'

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, int(port)))
        s.send(LOGIN_TEMPLATE % (struct.pack('b', 24 + len(login) + len(password)), login.encode('ascii'),
                                            (8 - len(login)) * b'\x00', password.encode('ascii'),
                                            (8 - len(password)) * b'\x00', login.encode('ascii'),
                                            password.encode('ascii'), str(int(time.time())).encode('ascii')))

        data = s.recv(128)
        status = -1
        if len(data) >= 10:
            if data[8] == 1:
                if data[9] == 4:
                    status = 2
                status = 1
            elif data[8] == 0:
                status = 0
            else:
                status = -1
        else:
            status = -1

        if status != -1:
            logging.info(f'[DAHUA] Target {target} success checked')
            return target
        logging.debug(f'[DAHUA] Target {target} failed checked')
        return False
    except:
        logging.debug(f'[DAHUA] Target {target} failed checked')
        return False
    
def hikka_checker(target, logging):
    try:
        response = requests.get(f'http://{target}/doc/page/login.asp', timeout=3, verify=False)
        if response.status_code == 200:
            if 'lausername' in response.text and 'lapassword' in response.text:
                logging.info(f'[HIKKA] Target {target} success checked')
                return target
        logging.debug(f'[HIKKA] Target {target} failed checked')
        return False
    except:
        logging.debug(f'[HIKKA] Target {target} failed checked')
        return False