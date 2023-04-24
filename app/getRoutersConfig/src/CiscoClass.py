from ipaddress import IPv4Network
import re

class Cisco:
    def __init__(self, net_connect):
        self.net_connect = net_connect

    def getipv4StaticRoutes(self) -> list:
        output = self.net_connect.send_command(f"show running-config | i ip route")

        v4_routes = []
        new_v4_routes = self.separate_section(r"(^.*ip route.*$)", output)

        for route in new_v4_routes:
            re_route = r'ip route( vrf (?P<vrf>\S+))? (?P<subnet_address>\d+.\d+.\d+.\d+) (?P<subnet_mask>\d+.\d+.\d+.\d+) (?P<gateway>\d+.\d+.\d+.\d+)( (?P<metric>\d+))?( tag (?P<tag>\d+))?( name (?P<name>(\S|\s)+))?' #(?!.*\btrack\b)

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

    def getSystemInformation(self) -> list:
        output = self.net_connect.send_command(f"show version")

        re_serie_version = r'Cisco IOS Software, (?P<serie>\S+) Software (\S+), Version (?P<version>\S+), RELEASE SOFTWARE \S+'
        re_hostname_uptime = r'(?P<hostname>\S+) uptime is( (?P<years>\d+) year(s)?,)?( (?P<weeks>\d+) week(s)?,)?( (?P<days>\d+) day(s)?,)?( (?P<hours>\d+) hour(s)?,)?( (?P<minutes>\d+) minute(s)?)?'
        re_system_image = r'System image file is "flash:(?P<system_image>\S+)"'
        re_serial_number = r'Processor board ID (?P<serial_number>\S+)'
        re_config_register = r'Configuration register is (?P<config_register>\S+)'

        match_serie_version = re.search(re_serie_version, output, flags=re.M)
        match_hostname_uptime = re.search(re_hostname_uptime, output, flags=re.M)
        match_system_image = re.search(re_system_image, output, flags=re.M)
        match_serial_number = re.search(re_serial_number, output, flags=re.M)
        match_config_register = re.search(re_config_register, output, flags=re.M)

        return {
            "serie": match_serie_version.group('serie'),
            "version": match_serie_version.group('version'),
            "hostname": match_hostname_uptime.group('hostname'),
            "uptime": {
                "years": int(match_hostname_uptime.group('years')) if match_hostname_uptime.group('years') else 0,
                "weeks": int(match_hostname_uptime.group('weeks')) if match_hostname_uptime.group('weeks') else 0,
                "days": int(match_hostname_uptime.group('days')) if match_hostname_uptime.group('days') else 0,
                "hours": int(match_hostname_uptime.group('hours')) if match_hostname_uptime.group('hours') else 0,
                "minutes": int(match_hostname_uptime.group('minutes')),
            },
            "system_image": match_system_image.group('system_image'),
            "serial_number": match_serial_number.group('serial_number'),
            "config_register": match_config_register.group('config_register'),
        }

    def separate_section(self, separator, content):
        if content == "":
            return []

        lines = re.split(separator, content, flags=re.M)

        if len(lines) == 1:
            msg = "Unexpected output data:\n{}".format(lines)
            raise ValueError(msg)

        lines.pop(0)

        if len(lines) % 2 != 0:
            msg = "Unexpected output data:\n{}".format(lines)
            raise ValueError(msg)

        lines_iter = iter(lines)

        try:
            new_lines = [line + next(lines_iter, '') for line in lines_iter]
        except TypeError:
            raise ValueError()
        return new_lines

    def getInterfaces(self):
        output_v4 = self.net_connect.send_command('show ip interface')
        v4_interfaces = [{
            "switched": [],
            "routed": []
        }]
        new_v4_interfaces = self.separate_section(r"(^.*line protocol is.*$)", output_v4)

        for interface in new_v4_interfaces:
            re_intf_name_state = r"^(?P<intf_name>\S+).+is.(?P<intf_state>.+)., line protocol is .(?P<intf_protocol_state>.+)$"
            re_intf_ip = r"Internet address is\s+(?P<ip_address>\d+.\d+.\d+.\d+)\/(?P<prefix_length>\d+)"

            match_intf = re.search(re_intf_name_state, interface, flags=re.M)

            intf_name = match_intf.group('intf_name')

            match_ip = re.findall(re_intf_ip, interface, flags=re.M)

            output_run = self.net_connect.send_command(f'show running-config interface {intf_name}')

            if not match_ip and re.search('FastEthernet|GigabitEthernet', intf_name):
                re_switchport = r"switchport ((mode )?(?P<switchport_mode>\S+))(( allowed)? vlan (?P<vlan>\S+))?"

                match_switchport = re.search(re_switchport, output_run, flags=re.M)

                if match_switchport:
                    v4_interfaces[0]["switched"].append({
                        "name": intf_name,
                        "switchport_mode": match_switchport.group('switchport_mode') if match_switchport.group('switchport_mode') else "access",
                        "vlan": match_switchport.group('vlan') if match_switchport.group('vlan') else "1"
                    })
                else:
                    v4_interfaces[0]["switched"].append({
                        "name": intf_name,
                        "switchport_mode": "access",
                        "vlan": "1"
                    })

            for ip_info in match_ip:
                # if ip_info:
                re_vrf = r"ip vrf forwarding (?P<vrf>\S+)"
                re_description = r"description (?P<description>.+)"

                match_vrf = re.search(re_vrf, output_run, flags=re.M)
                match_description = re.search(re_description, output_run, flags=re.M)

                vrf = match_vrf.group('vrf') if match_vrf else ""
                description = match_description.group('description') if match_description else ""

                v4_interfaces[0]["routed"].append({
                    "name": intf_name,
                    "description": description,
                    "ip": ip_info[0],
                    "mask": {
                        "octets": str(IPv4Network((0, ip_info[1])).netmask),
                        "cidr": int(ip_info[1])
                    },
                    "vrf": vrf
                })

        return v4_interfaces
    
    def getDhcp(self):
        output_v4 = self.net_connect.send_command('show run | s ip dhcp pool')
        res_dhcp = []
        options = []

        new_dhcp = self.separate_section(r"(^ip dhcp pool.*$)", output_v4)

        for dhcp in new_dhcp:
            re_dhcp_pool_name = r"^ip dhcp pool (?P<dhcp_pool_name>.+)$"
            re_network = r"network (?P<network_address>\d+.\d+.\d+.\d+) (?P<network_mask>\d+.\d+.\d+.\d+)"
            re_default_router = r"default-router (?P<default_router>\d+.\d+.\d+.\d+)"
            re_dns_server = r"dns-server (?P<dns_server>.+)"
            re_options = r"option (?P<code>\d+) (?P<string_type>\S+) (?P<string>\S+)"

            match_dhcp_pool_name = re.search(re_dhcp_pool_name, dhcp, flags=re.M)
            match_network = re.search(re_network, dhcp, flags=re.M)
            match_default_router = re.search(re_default_router, dhcp, flags=re.M)
            match_dns_server = re.search(re_dns_server, dhcp, flags=re.M)
            match_options = re.findall(re_options, dhcp, flags=re.M)

            if match_options:
                for option in match_options:
                    options.append({
                        "code": int(option[0]),
                        "string_type": option[1],
                        "string": str(option[2]).replace('"', '')
                    })

            res_dhcp.append({
                "name": match_dhcp_pool_name.group('dhcp_pool_name'),
                "network": {
                    "subnet_address": match_network.group('network_address'),
                    "mask": {
                        "octets": match_network.group('network_address'),
                        "cidr": IPv4Network((0, match_network.group('network_mask'))).prefixlen,
                    }
                },
                "default_router": match_default_router.group('default_router'),
                "dns_server": [i for i in match_dns_server.group('dns_server').strip().split(' ')],
                "option": options
            })

        return res_dhcp