import socket
from enum import Enum
from ipaddress import ip_address
from time import sleep
from typing import List, Union
import base64
import functools
import hashlib
from tools.utils import find

MAX_RETRIES = 2

DUMMY_ROUTE = "/0x8b6c42"
MAX_SCREENSHOT_TRIES = 2

# 401, 403: credentials are wrong but the route might be okay.
# 404: route is incorrect but the credentials might be okay.
# 200: stream is accessed successfully.
ROUTE_OK_CODES = [
    "RTSP/1.0 200",
    "RTSP/1.0 401",
    "RTSP/1.0 403",
    "RTSP/2.0 200",
    "RTSP/2.0 401",
    "RTSP/2.0 403",
]
CREDENTIALS_OK_CODES = ["RTSP/1.0 200", "RTSP/1.0 404", "RTSP/2.0 200", "RTSP/2.0 404"]


class AuthMethod(Enum):
    NONE = 0
    BASIC = 1
    DIGEST = 2


class Status(Enum):
    CONNECTED = 0
    TIMEOUT = 1
    UNIDENTIFIED = 100
    NONE = -1

    @classmethod
    def from_exception(cls, exception: Exception):
        if type(exception) is type(socket.timeout()) or type(exception) is type(
            TimeoutError()
        ):
            return cls.TIMEOUT
        else:
            return cls.UNIDENTIFIED


class RTSPClient:
    __slots__ = (
        "ip",
        "port",
        "credentials",
        "routes",
        "status",
        "auth_method",
        "last_error",
        "realm",
        "nonce",
        "socket",
        "timeout",
        "packet",
        "cseq",
        "data",
    )

    def __init__(
        self,
        ip: str,
        port: int = 554,
        timeout: int = 2,
        credentials: str = ":",
    ) -> None:
        try:
            ip_address(ip)
        except ValueError as e:
            raise e

        if port not in range(65536):
            raise ValueError(f"{port} is not a valid port")

        self.ip = ip
        self.port = port
        self.credentials = credentials
        self.routes: List[str] = []
        self.status: Status = Status.NONE
        self.auth_method: AuthMethod = AuthMethod.NONE
        self.last_error: Union[Exception, None] = None
        self.realm: str = ""
        self.nonce: str = ""
        self.socket = None
        self.timeout = timeout
        self.packet = ""
        self.cseq = 0
        self.data = ""

    @property
    def route(self):
        if len(self.routes) > 0:
            return self.routes[0]
        else:
            return ""

    @property
    def is_connected(self):
        return self.status is Status.CONNECTED

    @property
    def is_authorized(self):
        return "200" in self.data

    def connect(self, port: int = None):
        if self.is_connected:
            return True

        if port is None:
            port = self.port

        self.packet = ""
        self.cseq = 0
        self.data = ""
        retry = 0
        while retry < MAX_RETRIES and not self.is_connected:
            try:
                self.socket = socket.create_connection((self.ip, port), self.timeout)
            except Exception as e:
                self.status = Status.from_exception(e)
                self.last_error = e

                retry += 1
                sleep(1.5)
            else:
                self.status = Status.CONNECTED
                self.last_error = None

                return True

        return False

    def authorize(self, port=None, route=None, credentials=None):
        if not self.is_connected:
            return False

        if port is None:
            port = self.port
        if route is None:
            route = self.route
        if credentials is None:
            credentials = self.credentials

        self.cseq += 1
        self.packet = describe(
            self.ip, port, route, self.cseq, credentials, self.realm, self.nonce
        )
        try:
            self.socket.sendall(self.packet.encode())
            self.data = self.socket.recv(1024).decode()
        except Exception as e:
            self.status = Status.from_exception(e)
            self.last_error = e
            self.socket.close()

            return False

        if not self.data:
            return False

        if "Basic" in self.data:
            self.auth_method = AuthMethod.BASIC
        elif "Digest" in self.data:
            self.auth_method = AuthMethod.DIGEST
            self.realm = find("realm", self.data)
            self.nonce = find("nonce", self.data)
        else:
            self.auth_method = AuthMethod.NONE

        return True

    @staticmethod
    def get_rtsp_url(
        ip: str, port: Union[str, int] = 554, credentials: str = ":", route: str = "/"
    ):
        """Return URL in RTSP format."""
        if credentials != ":":
            ip_prefix = f"{credentials}@"
        else:
            ip_prefix = ""
        return f"rtsp://{ip_prefix}{ip}:{port}{route}"

    def __str__(self) -> str:
        return self.get_rtsp_url(self.ip, self.port, self.credentials, self.route)

    def __rich__(self) -> str:
        return f"{self.__str__()}"

@functools.lru_cache(maxsize=15)
def _basic_auth(credentials):
    encoded_cred = base64.b64encode(credentials.encode("ascii"))
    return f"Authorization: Basic {str(encoded_cred, 'utf-8')}"


@functools.lru_cache()
def _ha1(username, realm, password):
    return hashlib.md5(f"{username}:{realm}:{password}".encode("ascii")).hexdigest()


def _digest_auth(option, ip, port, path, credentials, realm, nonce):
    username, password = credentials.split(":")
    uri = f"rtsp://{ip}:{port}{path}"
    HA1 = _ha1(username, realm, password)
    HA2 = hashlib.md5(f"{option}:{uri}".encode("ascii")).hexdigest()
    response = hashlib.md5(f"{HA1}:{nonce}:{HA2}".encode("ascii")).hexdigest()

    return (
        "Authorization: Digest "
        f'username="{username}", '
        f'realm="{realm}", '
        f'nonce="{nonce}", '
        f'uri="{uri}", '
        f'response="{response}"'
    )


def describe(ip, port, path, cseq, credentials, realm=None, nonce=None):
    if credentials == ":":
        auth_str = ""
    elif realm:
        auth_str = (
            f"{_digest_auth('DESCRIBE', ip, port, path, credentials, realm, nonce)}\r\n"
        )
    else:
        auth_str = f"{_basic_auth(credentials)}\r\n"

    return (
        f"DESCRIBE rtsp://{ip}:{port}{path} RTSP/1.0\r\n"
        f"CSeq: {cseq}\r\n"
        f"{auth_str}"
        "User-Agent: Mozilla/5.0\r\n"
        "Accept: application/sdp\r\n"
        "\r\n"
    )

def rtsp_connect(target, port=None, route=None, credentials=None):
    if port is None:
        port = target.port
    if route is None:
        route = target.route
    if credentials is None:
        credentials = target.credentials

    connected = target.connect(port=port)
    if not connected:
        return False
    
    authorized = target.authorize(port=port, route=route.replace('\n', ''), credentials=credentials.replace('\n', ''))
    if not authorized:
        return False
    
    return True
