# -*- coding: utf-8 -*-
"""

This purpose of this module is to provide interface related classes, methods,
and attributes for Cisco device interfaces based on appropriate SNMP OIDs;
such as ifMIB; ipMIB; CISCO-STACK-MIB; CISCO-L2L3-INTERFACE-CONFIG-MIB, etc.
"""

import ipaddress
import re


class MissingParameterError(ValueError):
    pass


class CiscoPyInterfaces(list):
    pass


class CiscoPyInterface(object):
    def __init__(self, **kwargs):
        if 'interface_name' not in kwargs.keys():
            raise MissingParameterError('interface_name paramter not supplied')

        self.interface_name = kwargs['interface_name']


class CiscoPySwitchPhysicalInterface(CiscoPyInterface):
    def __init__(self, **kwargs):
        """

        :param interface_name:      The Switch Physical Interface name; type str
        :param mode:                The switchport mode; type str
        :param access_vlan:         The switchport access vlan; type int
        :param voice_vlan:          The switchport voice vlan; type int
        :param trunk_native_vlan:   The switchport trunk native vlan; type int
        :param trunk_allowed_vlan:  The switchport trunk allowed vlans;
                                    type list
        """
        super(CiscoPySwitchPhysicalInterface, self).__init__(**kwargs)
        self.mode = None
        self.access_vlan = 1
        self.voice_vlan = None
        self.trunk_native_vlan = 1
        self.trunk_allowed_vlan = []
        self.spanningtree_portfast = False
        self.spanningtree_bpduguard = False


class CiscoPySwitchVirtualInterface(CiscoPyInterface):
    def __init__(self, **kwargs):
        """

        :param interface_name:  The Switch Logical Interface name; type str
        :param ip_redirects:    True/False; type bool
        :param ip_unreachables: True/False; type bool
        :param ip_proxyarp:     True/False; type bool
        """
        super(CiscoPySwitchVirtualInterface, self).__init__(**kwargs)

        if ('ip_redirects' in kwargs.keys() and
                not isinstance(kwargs['ip_redirects'], bool)):
            raise TypeError('The ip_redirects parameter is not type bool')
        else:
            self.ip_redirects = kwargs.get('ip_redirects', False)

        if ('ip_unreachables' in kwargs.keys() and
                not isinstance(kwargs['ip_unreachables'], bool)):
            raise TypeError('The ip_unreachables parameter is not type bool')
        else:
            self.ip_redirects = kwargs.get('ip_unreachables', False)

        if ('ip_proxyarp' in kwargs.keys() and
                not isinstance(kwargs['ip_proxyarp'], bool)):
            raise TypeError('The ip_proxyarp parameter is not type bool')
        else:
            self.ip_redirects = kwargs.get('ip_proxyarp', False)


class CiscoPyIPv4Interface(ipaddress.IPv4Interface):
    def __init__(self, if_name, ipv4, **kwargs):
        """

        :param if_name:         interface name (or designation) as a string
        :param ipv4:            ipv4_address/ipv4_subnetmask as a string
        :param bandwidth:       interface bandwidth as a string
        :param description:     interface description as a string
        :param ip_redirects:    True/False
        :param ip_unreachables: True/False
        :param ip_proxyarp:     True/False
        """

        if '/' not in ipv4:
            raise ValueError('parameter ipv4 not in correct format')

        ip_regex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        if ip_regex.match(ipv4.split('/')[0]) is None:
            raise ValueError('the ip address of paramter ipv4 is not in dotted '
                             'notation.')

        if ip_regex.match(ipv4.split('/')[-1]) is None:
            raise ValueError('the subnet mask of paramter ipv4 is not in '
                             'dotted notation.')

        super(CiscoPyIPv4Interface, self).__init__(ipv4)

        self.interface_name = if_name

        if 'bandwidth' not in kwargs.keys():
            self.bandwidth = -1
        else:
            if not isinstance(kwargs.get('bandwidth'), int):
                raise TypeError('bandwidth parameter not type int')
            else:
                self.bandwidth = kwargs.get('bandwidth')

        if 'description' not in kwargs.keys():
            self.description = ''
        else:
            if not isinstance(kwargs.get('description'), str):
                raise TypeError('description parameter not type str')
            else:
                self.description = kwargs.get('description')

        if 'ip_redirects' not in kwargs.keys():
            self.ip_redirects = False
        else:
            if not isinstance(kwargs.get('ip_redirects'), bool):
                raise TypeError('ip_redirects parameter not type bool')
            else:
                self.ip_redirects = kwargs.get('ip_redirects')

        if 'ip_unreachables' not in kwargs.keys():
            self.ip_unreachables = False
        else:
            if not isinstance(kwargs.get('ip_unreachables'), bool):
                raise TypeError('ip_unreachables parameter not type bool')
            else:
                self.ip_unreachables = kwargs.get('ip_unreachables')

        if 'ip_proxyarp' not in kwargs.keys():
            self.ip_proxyarp = False
        else:
            if not isinstance(kwargs.get('ip_proxyarp'), bool):
                raise TypeError('ip_proxyarp parameter not type bool')
            else:
                self.ip_proxyarp = kwargs.get('ip_proxyarp')

