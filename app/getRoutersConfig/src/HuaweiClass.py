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
    
    def getIpv4StaticRoutes(self) -> list:
        output = self.net_connect.send_command(f"display current-configuration | i ip route-static")

        v4_routes = []
        new_v4_routes = separate_section(r"(^.*ip route-static.*$)", output)

        for route in new_v4_routes:
            re_route = r'ip route-static( vpn-instance (?P<vrf>\S+))? (?P<subnet_address>\d+.\d+.\d+.\d+) (?P<subnet_mask>\d+.\d+.\d+.\d+) (?P<gateway>\d+.\d+.\d+.\d+|\S+)( (?P<metric>\d+))?( tag (?P<tag>\d+))?( description (?P<name>(\S|\s)+))?' #(?!.*\btrack\b)

            match_route = re.search(re_route, route, flags=re.M)

            track = int(re.search(r'track\s+(\d+)', route).group(1)) if re.search(r'track\s+(\d+)', route) else ""
            route_without_track = re.sub(r'track\s+\d+', '', match_route.group('name').replace('"', '').replace('\n', '')) if match_route.group('name') else ""

            v4_routes.append({
                "subnet_address": match_route.group('subnet_address'),
                "mask": {
                    "octets": match_route.group('subnet_mask'),
                    "cidr": IPv4Network((0, match_route.group('subnet_mask'))).prefixlen
                },
                "vrf": match_route.group('vrf') if match_route.group('vrf') else "",
                "gateway": match_route.group('gateway'),
                "metric": int(match_route.group('metric')) if match_route.group('metric') else "",
                "tag": int(match_route.group('tag')) if match_route.group('tag') else "",
                "permanent": "true" if re.search(r'\bpermanent\b', route) else "false",
                "name": route_without_track.strip(),
                "track": track
            })

        return v4_routes