from hikvisionapi import Client

class HikClient():
    
    def __init__(self, ip, port=None, login=None, password=None):
        self.ip = ip
        self.port = port if port != None else 80
        self.login = login
        self.password = password
        self.url = f'http://{ip}:{port}'

    def connect(self):
        try:
            self.cam = Client(self.url, self.login, self.password)
            return True

        except:
            return False
        
    def get_count_channels(self):
        try:
            count_channels = len(self.cam.Streaming.channels)
            return count_channels
        except:
            return [101, 102, 201, 202]
        
    def get_snapshot(self, channel=101):
        try:
            response = self.cam.Streaming.channels[channel].picture(method='get', type='opaque_data')
            return response
        except:
            return False