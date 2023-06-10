from ipaddress import IPv4Network
from .tools import separate_section
import re

class Cisco:
    def __init__(self, net_connect):
        self.net_connect = net_connect

    def getIpv4StaticRoutes(self) -> list:
        output = self.net_connect.send_command(f"show running-config | i ip route")

        v4_routes = []
        new_v4_routes = separate_section(r"(^.*ip route.*$)", output)

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
        re_model = r'Cisco (?P<model>\S+) \(revision \S+\) with \S+ bytes of memory.'
        re_serial_number = r'Processor board ID (?P<serial_number>\S+)'
        re_config_register = r'Configuration register is (?P<config_register>\S+)'

        match_serie_version = re.search(re_serie_version, output, flags=re.M)
        match_hostname_uptime = re.search(re_hostname_uptime, output, flags=re.M)
        match_system_image = re.search(re_system_image, output, flags=re.M)
        match_model = re.search(re_model, output, flags=re.M)
        match_serial_number = re.search(re_serial_number, output, flags=re.M)
        match_config_register = re.search(re_config_register, output, flags=re.M)

        return {
            "serie": match_serie_version.group('serie'),
            "model": match_model.group('model'),
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

    

    def getInterfaces(self) -> list:
        output_v4 = self.net_connect.send_command('show ip interface')
        v4_interfaces = [{
            "switched": [],
            "routed": []
        }]
        new_v4_interfaces = separate_section(r"(^.*line protocol is.*$)", output_v4)

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
                re_acl_in = r"ip access-group (?P<acl_in>.+) in"
                re_acl_out = r"ip access-group (?P<acl_out>.+) out"

                match_vrf = re.search(re_vrf, output_run, flags=re.M)
                match_description = re.search(re_description, output_run, flags=re.M)
                match_acl_in = re.search(re_acl_in, output_run, flags=re.M)
                match_acl_out = re.search(re_acl_out, output_run, flags=re.M)

                vrf = match_vrf.group('vrf') if match_vrf else ""
                description = match_description.group('description') if match_description else ""
                acl_in = match_acl_in.group('acl_in') if match_acl_in else ""
                acl_out = match_acl_out.group('acl_out') if match_acl_out else ""

                v4_interfaces[0]["routed"].append({
                    "name": intf_name,
                    "description": description,
                    "ip": ip_info[0],
                    "mask": {
                        "octets": str(IPv4Network((0, ip_info[1])).netmask),
                        "cidr": int(ip_info[1])
                    },
                    "vrf": vrf,
                    "acl_in": acl_in,
                    "acl_out": acl_out
                })

        return v4_interfaces
    
    def getDhcp(self) -> list:
        output_v4 = self.net_connect.send_command('show run | s ip dhcp pool')
        res_dhcp = []
        options = []

        new_dhcp = separate_section(r"(^ip dhcp pool.*$)", output_v4)

        for dhcp in new_dhcp:
            re_dhcp_pool_name = r"^ip dhcp pool (?P<dhcp_pool_name>.+)$"
            re_network = r"(network (?P<network_address>\d+.\d+.\d+.\d+) (?P<network_mask>\d+.\d+.\d+.\d+))?"
            re_default_router = r"(default-router (?P<default_router>\d+.\d+.\d+.\d+))?"
            re_dns_server = r"(dns-server (?P<dns_server>.+))?"
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
                    "subnet_address": match_network.group('network_address') if match_network.group('network_address') else "",
                    "mask": {
                        "octets": match_network.group('network_address') if match_network.group('network_address') else "",
                        "cidr": IPv4Network((0, match_network.group('network_mask'))).prefixlen if match_network.group('network_address') else "",
                    }
                },
                "default_router": match_default_router.group('default_router') if match_default_router.group('default_router') else "",
                "dns_server": [i for i in match_dns_server.group('dns_server').strip().split(' ')] if match_dns_server.group('dns_server') else "",
                "option": options
            })

        return res_dhcp
    
    def getIpv4Acl(self) -> list:
        output_v4 = self.net_connect.send_command('show ip access-lists')
        res_ipv4_acl = []

        new_acl = separate_section(r"(^.*IP access list.*$)", output_v4)

        for acl in new_acl:
            acl_rule = []
            re_acl_type_name = r"^(?P<acl_type>\S+) IP access list (?P<acl_name>.+)"
            re_acl_rule = r"(?P<sequence_number>\d+) (?P<pass>\S+) (?P<protocol>\S+) (any|host \d+.\d+.\d+.\d+|\d+.\d+.\d+.\d+ \d+.\d+.\d+.\d+)( eq (\S+|\d+))? (any|host \d+.\d+.\d+.\d+|\d+.\d+.\d+.\d+ \d+.\d+.\d+.\d+)( eq (\S+|\d+))?( \((\d+) matches\))?"

            match_acl_type_name = re.search(re_acl_type_name, acl, flags=re.M)
            match_acl_rule = re.findall(re_acl_rule, acl, flags=re.M)

            if match_acl_rule:
                for acl in match_acl_rule:
                    acl_rule.append({
                        "sequence_number": int(acl[0]),
                        "pass": acl[1],
                        "protocol": acl[2],
                        "source": acl[3],
                        "source_port": acl[5] if acl[4] else "all",
                        "destination": acl[6],
                        "destination_port": acl[8] if acl[8] else "all",
                        "macthes": int(acl[10]) if acl[10] else 0,
                        # "option": acl[5] if acl[5] else ""
                    })

            if match_acl_type_name.group('acl_name') not in ["97", "98", "99", "ACL-IP-MANAGEMENT", "ACL-ControlPlane"]:
                res_ipv4_acl.append({
                    "type": match_acl_type_name.group('acl_type'),
                    "name": match_acl_type_name.group('acl_name'),
                    "rule": acl_rule
                })

        return res_ipv4_acl