from ipaddress import IPv4Network, ip_address, ip_network
from .tools import separate_section
import re


class Huawei:
    def __init__(self, net_connect):
        self.net_connect = net_connect
        self.net_connect.config_mode()

    def display_ip_interface(self):
        output_v4 = self.net_connect.send_command('display ip interface')
        v4_interfaces = {}
        new_v4_interfaces = self.separate_section(
            r"(^(?!Line protocol).*current state.*$)", output_v4)

        for interface in new_v4_interfaces:
            re_intf_name_state = r"^(?!Line protocol)(?P<intf_name>\S+).+current state\W+(?P<intf_state>.+)$"
            re_intf_ip = r"Internet Address is\s+(?P<ip_address>\d+.\d+.\d+.\d+)\/(?P<prefix_length>\d+)"

            match_intf = re.search(re_intf_name_state, interface, flags=re.M)
            if match_intf is None:
                msg = "Unexpected interface format: {}".format(interface)
                raise ValueError(msg)
            intf_name = match_intf.group('intf_name')
            match_ip = re.findall(re_intf_ip, interface, flags=re.M)

            for ip_info in match_ip:
                v4_interfaces[intf_name] = f"{ip_info[0]}/{ip_info[1]}"

        return v4_interfaces
    
    