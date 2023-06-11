[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/netmiko.svg)](https://img.shields.io/pypi/pyversions/netmiko)

# What it does ?
This return Cisco configuration and information like :
 - Sytem informations
 - Static routes
 - Interfaces
 - DHCP
 - ACL

# Informations
bastion_ip and bastion_port are optional

# Get system informations
```python
from getRoutersConfig import setInformations

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

system_information = router.getSystemInformation()

router.disconnect()
```

The Schema is :
```json
{
    "serie": "C800",
    "model": "C891F-K9",
    "version": "15.4(3)M6",
    "hostname": "THE_ROUTER",
    "uptime": {
        "years": 0,
        "weeks": 1,
        "days": 1,
        "hours": 11,
        "minutes": 25
    },
    "system_image": "c800-universalk9-mz.SPA.154-3.M6.bin",
    "serial_number": "FCZ1234A5BC",
    "config_register": "0x2102"
}
```

# Get Ipv4 static routes
```python
from getRoutersConfig import setInformations

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

static_routes = router.getIpv4StaticRoutes()

router.disconnect()
```

The Schema is :
```json
[
    {
        "subnet_address": "1.1.1.1",
        "mask": {
        "octets": "255.255.255.255",
        "cidr": 29
        },
        "vrf": "TEST",
        "gateway": "2.2.2.2",
        "metric": 250,
        "tag": 408,
        "permanent": "false",
        "name": "the description",
        "track": 20
    },
    ...
]
```

# Get interfaces
```python
from getRoutersConfig import setInformations

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

interfaces = router.getInterfaces()

router.disconnect()
```

The Schema is :
```json

{
    "switched": [
        {
          "name": "FastEthernet0",
          "switchport_mode": "access",
          "vlan": "1"
        },
        ...
    ],
    "routed": [
        {
          "name": "FastEthernet4",
          "description": "",
          "ip": "192.168.1.101",
          "mask": {
            "octets": "255.255.255.0",
            "cidr": 24
          },
          "vrf": ""
        },
        ...
    ]
},
```

# Get DHCP
```python
from getRoutersConfig import setInformations

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

dhcp = router.getDhcp()

router.disconnect()
```

The Schema is :
```json

[
    {
        "name": "DATA",
        "network": {
            "subnet_address": "10.0.0.0",
            "mask": {
                "octets": "10.0.0.0",
                "cidr": 24
            }
        },
        "default_router": "10.0.0.1",
        "dns_server": [
            "8.8.8.8",
            ...
        ],
        "option": [
            {
                "code": 2,
                "string_type": "ascii",
                "string": "opt2"
            },
            ...
        ]
    },
    ...
]
```

# Get ACL
```python
from getRoutersConfig import setInformations

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

acl = router.getIpv4Acl()

router.disconnect()
```

The Schema is :
```json

[
    {
        "type": "Extended",
        "name": "acl-premium",
        "rule": [
            {
                "sequence_number": 10,
                "pass": "permit",
                "protocol": "udp",
                "source": "any",
                "source_port": "all",
                "destination": "host 192.168.10.3",
                "destination_port": "snmp",
                "macthes": 2417837
            },
            ...
        ]
    },
    ...
]
```

# Get full configuration
```python
from getRoutersConfig import setInformations

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

config = router.getFullConfiguration()

router.disconnect()
```

The Schema is :
```json

{
    "system": {},
    "ipv4StaticRoutes": [],
    "interfaces": [],
    "dhcp": [],
    "acl": []
}
```
