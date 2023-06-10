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

    def disconnect(self):
        self.net_connect.disconnect()

    def getFullConfiguration(self):
        return {
            "system": self.router.getSystemInformation(),
            "ipv4StaticRoutes": self.router.getIpv4StaticRoutes(),
            "interfaces": self.router.getInterfaces(),
            "dhcp": self.router.getDhcp(),
            "acl": self.router.getIpv4Acl()
        }

    def getIpv4StaticRoutes(self):
        return self.router.getIpv4StaticRoutes()
    
    def getSystemInformation(self):
        return self.router.getSystemInformation()
    
    def getInterfaces(self):
        return self.router.getInterfaces()
    
    def getDhcp(self):
        return self.router.getDhcp()
    
    def getIpv4Acl(self):
        return self.router.getIpv4Acl()