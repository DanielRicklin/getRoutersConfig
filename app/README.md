[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/netmiko.svg)](https://img.shields.io/pypi/pyversions/netmiko)

# What it does ?
This return Cisco configuration and information like :
 - Sytem informations
 - Static routes
 - Interfaces
 - DHCP

# Get system informations
```python
from getRoutersConfig import setInformations
import json

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

system_information = router.getSystemInformation()
```

The Schema is :
```json
{
    "serie": "C870",
    "version": "12.4(24)T4",
    "hostname": "HomeC871",
    "uptime": {
        "years": 0,
        "weeks": 0,
        "days": 2,
        "hours": 2,
        "minutes": 44
}
```

# Get static routes
```python
from getRoutersConfig import setInformations
import json

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

static_routes = router.getStaticRoutes()
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
import json

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

interfaces = router.getInterfaces()
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
import json

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

dhcp = router.getDhcp()
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

# Get full configuration
```python
from getRoutersConfig import setInformations
import json

router = setInformations(host_ip: str='', host_port: str='22', host_snmp_community: str='public', user: str='', password: str='', bastion_ip: str='', bastion_port: str='')

config = router.getFullConfiguration()
```

The Schema is :
```json

{
    "system": {},
    "ipv4StaticRoutes": [],
    "interfaces": [],
    "dhcp": []
}
```