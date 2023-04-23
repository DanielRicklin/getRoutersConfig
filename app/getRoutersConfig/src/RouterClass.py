from .HuaweiClass import Huawei
from .CiscoClass import Cisco


class Router:
    def __init__(self, router_type, net_connect):
        self.router_type = router_type
        self.net_connect = net_connect
        if self.router_type == "huawei":
            self.router = Huawei(self.net_connect)
        elif self.router_type == "cisco_ios":
            self.router = Cisco(self.net_connect)

    def getFullConfiguration(self):
        return {
            "system": self.router.getSystemInformation(),
            "ipv4StaticRoutes": self.router.getipv4StaticRoutes(),
            "interfaces": self.router.getInterfaces()
        }

    def getipv4StaticRoutes(self):
        return self.router.getipv4StaticRoutes()
    
    def getSystemInformation(self):
        return self.router.getSystemInformation()
    
    def getInterfaces(self):
        return self.router.getInterfaces()