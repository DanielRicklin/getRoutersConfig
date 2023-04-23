from ipaddress import IPv4Network, ip_address, ip_network
import re


class Huawei:
    def __init__(self, net_connect):
        self.net_connect = net_connect
        self.net_connect.config_mode()

    def add_ipv4_static_route(self, subnet_source, gateway_route):
        self.net_connect.send_command(
            f'ip route-static vpn-instance VPN {IPv4Network(subnet_source).network_address} {IPv4Network(subnet_source).netmask} {gateway_route}', cmd_verify=False)
        self.net_connect.exit_config_mode()
        self.net_connect.save_config()

    def remove_ipv4_static_route(self, subnet, gateway):
        self.net_connect.send_command(
            f'undo ip route-static vpn-instance VPN {IPv4Network(subnet).network_address} {IPv4Network(subnet).netmask} {gateway}', cmd_verify=False)
        self.net_connect.exit_config_mode()
        self.net_connect.save_config()

    def show_ipv4_routes(self, subnet):
        self.net_connect.send_command(
            f"display ip routing-table vpn-instance VPN {IPv4Network(subnet).network_address}")

    def separate_section(self, separator, content):
        if content == "":
            return []

        # Break output into per-interface sections
        interface_lines = re.split(separator, content, flags=re.M)

        if len(interface_lines) == 1:
            msg = "Unexpected output data:\n{}".format(interface_lines)
            raise ValueError(msg)

        # Get rid of the blank data at the beginning
        interface_lines.pop(0)

        # Must be pairs of data (the separator and section corresponding to it)
        if len(interface_lines) % 2 != 0:
            msg = "Unexpected output data:\n{}".format(interface_lines)
            raise ValueError(msg)

        # Combine the separator and section into one string
        intf_iter = iter(interface_lines)

        try:
            new_interfaces = [line + next(intf_iter, '') for line in intf_iter]
        except TypeError:
            raise ValueError()
        return new_interfaces

    def add_dhcp_pool(self, dhcp_pool_name, ip, mac_address):
        new_mac_address = '-'.join([mac_address[i:i+4]
                                   for i in range(0, len(mac_address), 4)])
        interfaces = self.display_ip_interface()
        for interface_name, subnet in interfaces.items():
            if ip_address(ip) in ip_network(subnet, False):
                DHCP_CONFIGS_COMMANDS_HUAWEI = [
                    f"interface {interface_name}",
                    f"dhcp select interface",
                    f"dhcp server static-bind ip-address {ip} mac-address {new_mac_address}",
                ]
                self.net_connect.send_config_set(
                    DHCP_CONFIGS_COMMANDS_HUAWEI, cmd_verify=False)
                self.net_connect.exit_config_mode()
                self.net_connect.save_config()

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

    def show_config_filter(self, filter):
        return self.net_connect.send_command(f'display current-configuration | {filter}', cmd_verify=False)