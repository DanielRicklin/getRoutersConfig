from ipaddress import IPv4Network, ip_address, ip_network
from .tools import separate_section
import re


class Huawei:
    def __init__(self, net_connect):
        self.net_connect = net_connect
        self.net_connect.config_mode()

    def getSystemInformation(self) -> list:
        output = self.net_connect.send_command("display version")
        hostname = self.net_connect.send_command("display current-configuration | i sysname")
        serial_number = self.net_connect.send_command("display esn")

        re_serie_version_image = r'VRP \(R\) software, Version (?P<version>\S+) \((?P<serie>\S+) (?P<system_image>\S+)\)'
        re_hostname = r'sysname (?P<hostname>\S+)'
        re_model_uptime = r'Huawei (?P<model>\S+) Router uptime is( (?P<years>\d+) year(s)?,)?( (?P<weeks>\d+) week(s)?,)?( (?P<days>\d+) day(s)?,)?( (?P<hours>\d+) hour(s)?,)?( (?P<minutes>\d+) minute(s)?)?'
        re_serial_number = r'ESN of device: (?P<serial_number>\S+)'

        match_serie_version_image = re.search(re_serie_version_image, output, flags=re.M)
        match_hostname = re.search(re_hostname, hostname, flags=re.M)
        match_model_uptime = re.search(re_model_uptime, output, flags=re.M)
        match_serial_number = re.search(re_serial_number, serial_number, flags=re.M)

        print(match_serie_version_image)
        print(match_hostname)
        print(match_serial_number)


        return {
            "serie": match_serie_version_image.group('serie'),
            "model": match_model_uptime.group('model'),
            "version": match_serie_version_image.group('version'),
            "hostname": match_hostname.group('hostname'),
            "uptime": {
                "years": int(match_model_uptime.group('years')) if match_model_uptime.group('years') else 0,
                "weeks": int(match_model_uptime.group('weeks')) if match_model_uptime.group('weeks') else 0,
                "days": int(match_model_uptime.group('days')) if match_model_uptime.group('days') else 0,
                "hours": int(match_model_uptime.group('hours')) if match_model_uptime.group('hours') else 0,
                "minutes": int(match_model_uptime.group('minutes')),
            },
            "system_image": match_serie_version_image.group('system_image'),
            "serial_number": match_serial_number.group('serial_number'),
            # "config_register": "",
        }

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