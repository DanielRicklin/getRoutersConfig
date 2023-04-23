from netmiko import ConnectHandler, redispatch
import time
from .RouterClass import Router
from pysnmp.hlapi import *

def setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='') -> Router:
    if not bastion_ip:
        device_type: str = getDeviceType(host_ip, host_snmp_community)

    host = {
        'device_type': device_type if not bastion_ip else "terminal_server",
        'ip': host_ip if not bastion_ip else bastion_ip,
        'username': user,
        'password': password,
        'port': host_port if not bastion_ip else bastion_port,
    }

    net_connect = ConnectHandler(**host)

    if bastion_ip:
        output = net_connect.write_channel(f"snmpwalk -v2c -c covareck {host_ip} SNMPv2-MIB::sysDescr\n")

        if "huawei" in output.lower():
            device_type: str = "huawei"
        elif "cisco" in output.lower():
            device_type: str = "cisco_ios"

        net_connect.write_channel(f"ssh {host_ip}\r\n")

        time.sleep(2)

        output = net_connect.read_channel()

        if 'password' in output.lower():
            net_connect.write_channel(password)

        redispatch(net_connect, device_type=device_type)

    return Router(device_type, net_connect)

def getDeviceType(ip, snmp_community):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(snmp_community, mpModel=0),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            output = ' = '.join([x.prettyPrint() for x in varBind])
            if "huawei" in output.lower():
                return "huawei"
            elif "cisco" in output.lower():
                return "cisco_ios"
            raise ValueError("The router needs to be a Cisco_ios or Huawei")

# net_connect.disconnect()
